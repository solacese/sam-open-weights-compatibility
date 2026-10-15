#!/usr/bin/env python3
"""Endpoint smoke checks. Exit 0=pass, 1=failed check, 2=configuration error."""
import argparse
import copy
import datetime
import json
import os
import pathlib
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request

LIMIT = 8 * 1024 * 1024
TOOLS = [{"type": "function", "function": {
    "name": "get_weather", "description": "Read current weather for a city.",
    "parameters": {"type": "object", "properties": {"city": {"type": "string"}},
                   "required": ["city"], "additionalProperties": False}}}]
MESSAGES = [{"role": "user", "content": "Use get_weather to read the current weather in Copenhagen. Do not guess."}]


class ProbeFailure(Exception):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Do not forward an inference credential to a redirected endpoint.
        return None


def bare_model(value):
    # A hub namespace is not necessarily a provider prefix.
    return value[len("openai/"):] if value.startswith("openai/") else value


def validate_call(call):
    if not isinstance(call, dict):
        raise ProbeFailure("tool call is not an object")
    if not isinstance(call.get("id"), str) or not call["id"].strip():
        raise ProbeFailure("missing tool call ID")
    if call.get("type") != "function":
        raise ProbeFailure("wrong tool call type")
    function = call.get("function", {})
    if function.get("name") != "get_weather":
        raise ProbeFailure("wrong tool name")
    try:
        args = json.loads(function["arguments"])
    except (KeyError, TypeError, ValueError):
        raise ProbeFailure("arguments are not JSON text") from None
    if args != {"city": "Copenhagen"}:
        raise ProbeFailure("arguments do not match expected schema and city")
    return call


def message_call(body):
    if not isinstance(body, dict) or body.get("error"):
        raise ProbeFailure("endpoint returned an error payload")
    choices = body.get("choices", [])
    if len(choices) != 1 or choices[0].get("finish_reason") != "tool_calls":
        raise ProbeFailure("missing tool_calls finish reason")
    message = choices[0].get("message", {})
    calls = message.get("tool_calls", [])
    if len(calls) != 1:
        raise ProbeFailure("expected exactly one native tool call")
    validate_call(calls[0])
    return message


def parse_sse(lines):
    """Parse data events, allowing comments, CRLF, usage events and split calls."""
    calls = {}
    terminal = None
    done = False
    data = []

    def event(parts):
        nonlocal terminal, done
        payload = "\n".join(parts)
        if payload == "[DONE]":
            done = True
            return
        if done:
            raise ProbeFailure("data event after DONE")
        try:
            item = json.loads(payload)
        except ValueError:
            raise ProbeFailure("invalid SSE JSON") from None
        if not isinstance(item, dict) or item.get("error"):
            raise ProbeFailure("SSE error payload")
        for choice in item.get("choices", []):
            if choice.get("index") != 0:
                raise ProbeFailure("unexpected choice index")
            if terminal is not None:
                raise ProbeFailure("choice data after finish reason")
            if choice.get("finish_reason") is not None:
                terminal = choice["finish_reason"]
            for delta in choice.get("delta", {}).get("tool_calls", []):
                index = delta.get("index")
                if not isinstance(index, int) or isinstance(index, bool) or index < 0:
                    raise ProbeFailure("missing/invalid tool index")
                call = calls.setdefault(index, {"id": "", "type": "function", "function": {"name": "", "arguments": ""}})
                if delta.get("id"):
                    if call["id"] and call["id"] != delta["id"]:
                        raise ProbeFailure("tool call ID changed")
                    call["id"] = delta["id"]
                if delta.get("type"):
                    call["type"] = delta["type"]
                function = delta.get("function", {})
                for field in ("name", "arguments"):
                    fragment = function.get(field)
                    if fragment is not None:
                        if not isinstance(fragment, str):
                            raise ProbeFailure("non-text tool delta")
                        call["function"][field] += fragment

    for raw in lines:
        try:
            line = raw.decode("utf-8").rstrip("\r\n") if isinstance(raw, bytes) else raw.rstrip("\r\n")
        except UnicodeDecodeError:
            raise ProbeFailure("invalid SSE encoding") from None
        if not line:
            if data:
                event(data)
                data = []
        elif line.startswith("data:"):
            value = line[5:]
            data.append(value[1:] if value.startswith(" ") else value)
    if data:
        event(data)
    if not done or terminal != "tool_calls" or not calls:
        raise ProbeFailure("incomplete tool-call stream")
    if sorted(calls) != list(range(len(calls))):
        raise ProbeFailure("non-contiguous tool indices")
    ids = [call["id"] for call in calls.values()]
    if len(ids) != len(set(ids)):
        raise ProbeFailure("duplicate tool call IDs")
    return [calls[index] for index in sorted(calls)]


class Client:
    def __init__(self, base, key, timeout):
        parsed = urllib.parse.urlsplit(base)
        if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("API base must be http(s), without URL credentials, query or fragment")
        self.url = base.rstrip("/") + "/chat/completions"
        self.key, self.timeout = key, timeout
        self.opener = urllib.request.build_opener(NoRedirect())

    def request(self, payload, stream=False):
        headers = {"Content-Type": "application/json", "Accept": "text/event-stream" if stream else "application/json"}
        if self.key:
            headers["Authorization"] = "Bearer " + self.key
        request = urllib.request.Request(self.url, data=json.dumps(payload).encode(), headers=headers)
        started = time.monotonic()
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                def chunks():
                    size = 0
                    while True:
                        # read1 performs at most one underlying read. A peer trickling
                        # an unfinished SSE line cannot reset the total budget forever.
                        chunk = response.read1(65536)
                        if time.monotonic() - started > self.timeout:
                            raise ProbeFailure("response exceeded time budget")
                        if not chunk:
                            break
                        size += len(chunk)
                        if size > LIMIT:
                            raise ProbeFailure("response exceeded size budget")
                        yield chunk

                if stream:
                    if "text/event-stream" not in response.headers.get("Content-Type", ""):
                        raise ProbeFailure("stream response is not text/event-stream")

                    def lines():
                        pending = b""
                        for chunk in chunks():
                            pending += chunk
                            parts = pending.split(b"\n")
                            pending = parts.pop()
                            for line in parts:
                                yield line + b"\n"
                        if pending:
                            yield pending
                    return parse_sse(lines())
                return json.loads(b"".join(chunks()))
        except urllib.error.HTTPError as exc:
            raise ProbeFailure(f"HTTP {exc.code}") from None
        except (urllib.error.URLError, OSError, TimeoutError):
            raise ProbeFailure("network/TLS/timeout error") from None
        except ValueError:
            raise ProbeFailure("invalid response JSON") from None


def run(client, model, extra):
    # Overrides are limited to model generation settings; the checked contract is fixed.
    reserved = {"model", "tools", "tool_choice", "messages", "stream", "n"}
    if reserved.intersection(extra):
        raise ValueError("SAM_TEST_EXTRA_BODY must not override probe contract fields")
    request = {"max_tokens": 4096, **extra, "model": model, "tools": TOOLS,
               "tool_choice": "auto", "messages": MESSAGES}
    checks = []
    assistant = None
    for gate in ("H1", "H2", "H3"):
        start = time.monotonic()
        try:
            if gate == "H1":
                assistant = message_call(client.request(request))
            elif gate == "H2":
                calls = client.request({**request, "stream": True}, stream=True)
                if len(calls) != 1:
                    raise ProbeFailure("expected one streamed call")
                validate_call(calls[0])
            else:
                if assistant is None:
                    raise ProbeFailure("H3 cannot run without a valid H1 assistant turn")
                receipt = "receipt_" + secrets.token_hex(12)
                messages = copy.deepcopy(MESSAGES)
                messages[0]["content"] += " In your final answer repeat the exact receipt and temp_c returned by the tool."
                messages += [assistant, {"role": "tool", "tool_call_id": assistant["tool_calls"][0]["id"],
                                         "content": json.dumps({"city": "Copenhagen", "temp_c": 17.43, "receipt": receipt})}]
                result = client.request({**request, "messages": messages})
                if not isinstance(result, dict) or result.get("error"):
                    raise ProbeFailure("tool-result error payload")
                choices = result.get("choices", [])
                if len(choices) != 1 or choices[0].get("finish_reason") != "stop":
                    raise ProbeFailure("tool-result turn did not finish normally")
                message = choices[0].get("message", {})
                answer = message.get("content") or ""
                if message.get("tool_calls") or receipt not in answer or "17.43" not in answer:
                    raise ProbeFailure("tool result not reproduced or tool was called again")
            checks.append({"gate": gate, "status": "pass", "seconds": round(time.monotonic() - start, 3)})
        except (ProbeFailure, KeyError, TypeError, AttributeError, IndexError) as exc:
            detail = str(exc) if isinstance(exc, ProbeFailure) else "malformed protocol response"
            checks.append({"gate": gate, "status": "fail", "detail": detail,
                           "seconds": round(time.monotonic() - start, 3)})
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=pathlib.Path)
    args = parser.parse_args()
    try:
        model = os.environ.get("SAM_TEST_BARE_MODEL") or bare_model(os.environ["SAM_TEST_MODEL"])
        if not model.strip():
            raise ValueError("empty model ID")
        timeout = float(os.environ.get("SAM_TEST_TIMEOUT", "120"))
        if not 0 < timeout <= 3600:
            raise ValueError("timeout must be within (0, 3600] seconds")
        extra = json.loads(os.environ.get("SAM_TEST_EXTRA_BODY", "{}"))
        if not isinstance(extra, dict):
            raise ValueError("SAM_TEST_EXTRA_BODY must be an object")
        client = Client(os.environ["SAM_TEST_API_BASE"], os.environ.get("SAM_TEST_API_KEY", ""), timeout)
        checks = run(client, model, extra)
    except (ValueError, KeyError):
        print("Configuration error: set SAM_TEST_MODEL and SAM_TEST_API_BASE; check timeout and extra-body JSON. No request details logged.")
        return 2
    passed = all(check["status"] == "pass" for check in checks)
    report = {"schema_version": 1, "evidence_level": "endpoint-smoke-only", "model": model,
              "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "checks": checks,
              "result": "pass" if passed else "fail", "sam_validation": "not-run"}
    for check in checks:
        print(f"{check['gate']}: {check['status'].upper()}" + (" - " + check["detail"] if "detail" in check else ""))
    if args.report:
        # Newly created files are private; do not change permissions of existing user files.
        fd = os.open(args.report, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as output:
            json.dump(report, output, indent=2)
            output.write("\n")
    print("Endpoint smoke checks complete. Real SAM and production qualification remain required.")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
