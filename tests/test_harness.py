"""Synthetic harness tests; passing tests do not qualify any actual model."""
import contextlib
import copy
import hashlib
import http.server
import importlib.util
import io
import json
import os
import pathlib
import subprocess
import tempfile
import threading
import time
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parent.parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


probe = module("probe", "scripts/probe.py")
trace_check = module("trace_check", "scripts/check-sam-trace.py")


def call(cid="a"):
    return {"id": cid, "type": "function", "function": {"name": "get_weather", "arguments": '{"city":"Copenhagen"}'}}


def event(delta=None, finish=None):
    return {"choices": [{"index": 0, "delta": delta or {}, "finish_reason": finish}]}


def sse(items):
    return ("\r\n".join(": heartbeat\r\n\r\n" if x == "comment" else "data: " + (x if isinstance(x, str) else json.dumps(x)) + "\r\n" for x in items) + "\r\n").encode().splitlines(keepends=True)


def stream_items():
    return [event({"tool_calls": [{"index": 0, "id": "a", "type": "function", "function": {"name": "get_", "arguments": '{"ci'}}]}),
            event({"tool_calls": [{"index": 0, "function": {"name": "weather", "arguments": 'ty":"Copenhagen"}'}}]}),
            event(finish="tool_calls"), {"choices": [], "usage": {"total_tokens": 8}}, "[DONE]"]


class ProtocolTests(unittest.TestCase):
    def test_provider_prefix_preserves_hub_namespace(self):
        self.assertEqual(probe.bare_model("Qwen/model"), "Qwen/model")
        self.assertEqual(probe.bare_model("openai/openai/gpt-oss-20b"), "openai/gpt-oss-20b")

    def test_schema_checks_reject_false_passes(self):
        for bad in ({}, {**call(), "id": ""}, {**call(), "function": {"name": "get_weather", "arguments": '{"city":42}'}},
                    {**call(), "function": {"name": "get_weather", "arguments": '{"city":"Berlin"}'}},
                    {**call(), "function": {"name": "get_weather", "arguments": '{"city":"Copenhagen","injected":true}'}}):
            with self.subTest(bad=bad), self.assertRaises(probe.ProbeFailure):
                probe.validate_call(bad)

    def test_sse_fragments_comments_usage_and_crlf(self):
        self.assertEqual(probe.parse_sse(sse(["comment", *stream_items()])), [call()])

    def test_interleaved_tool_indices_are_kept_separate(self):
        items = [event({"tool_calls": [{"index": 1, "id": "b", "function": {"name": "other", "arguments": '{"b":'}},
                                      {"index": 0, "id": "a", "function": {"name": "first", "arguments": '{"a":'}}]}),
                 event({"tool_calls": [{"index": 0, "function": {"arguments": '1}'}}, {"index": 1, "function": {"arguments": '2}'}}]}),
                 event(finish="tool_calls"), "[DONE]"]
        result = probe.parse_sse(sse(items))
        self.assertEqual([c["id"] for c in result], ["a", "b"])
        self.assertEqual([json.loads(c["function"]["arguments"]) for c in result], [{"a": 1}, {"b": 2}])

    def test_incomplete_and_error_streams_fail(self):
        cases = [stream_items()[:-1], [{"error": {"message": "secret-not-to-log"}}], ["not-json"],
                 [event(finish="length"), "[DONE]"],
                 [event({"tool_calls": [{"function": {"name": "get_weather"}}]}), "[DONE]"],
                 [*stream_items()[:-2], event({"content": "late"}), "[DONE]"]]
        for items in cases:
            with self.subTest(items=items), self.assertRaises(probe.ProbeFailure):
                probe.parse_sse(sse(items))

    def test_duplicate_ids_fail(self):
        items = [event({"tool_calls": [{"index": 0, "id": "same"}, {"index": 1, "id": "same"}]}), event(finish="tool_calls"), "[DONE]"]
        with self.assertRaises(probe.ProbeFailure):
            probe.parse_sse(sse(items))

    def test_recalled_tool_and_canned_temperature_fail_h3(self):
        class Fake:
            def request(self, body, stream=False):
                if stream:
                    return [call()]
                if len(body["messages"]) == 1:
                    return {"choices": [{"finish_reason": "tool_calls", "message": {"role": "assistant", "tool_calls": [call()]}}]}
                return {"choices": [{"finish_reason": "stop", "message": {"content": "17.43 degrees"}}]}
        results = probe.run(Fake(), "test", {})
        self.assertEqual([r["status"] for r in results], ["pass", "pass", "fail"])

    def test_contract_override_is_rejected(self):
        with self.assertRaises(ValueError):
            probe.run(None, "test", {"tools": []})


class Handler(http.server.BaseHTTPRequestHandler):
    mode = "valid"
    seen_models = []

    def log_message(self, *_):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        type(self).seen_models.append(body["model"])
        if self.mode == "http-error":
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'secret-http-error-body')
            return
        if self.mode == "redirect":
            self.send_response(302)
            self.send_header("Location", "/must-not-follow")
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream" if body.get("stream") else "application/json")
        self.end_headers()
        if body.get("stream") and self.mode == "trickle":
            try:
                for _ in range(20):
                    self.wfile.write(b":")
                    self.wfile.flush()
                    time.sleep(0.02)
            except (BrokenPipeError, ConnectionResetError):
                pass
        elif body.get("stream"):
            self.wfile.write(b"".join(sse(stream_items())))
        elif len(body["messages"]) == 1:
            self.wfile.write(json.dumps({"choices": [{"finish_reason": "tool_calls", "message": {"role": "assistant", "tool_calls": [call()]}}]}).encode())
        else:
            result = json.loads(body["messages"][-1]["content"])
            text = f"{result['receipt']}: {result['temp_c']}"
            self.wfile.write(json.dumps({"choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": text}}]}).encode())


class HTTPTests(unittest.TestCase):
    def exercise(self, mode):
        Handler.mode = mode
        Handler.seen_models = []
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as temp:
                report = pathlib.Path(temp) / "result.json"
                env = {k: v for k, v in os.environ.items() if not k.startswith("SAM_TEST_")}
                env.update(SAM_TEST_MODEL="openai/test/model", SAM_TEST_API_BASE=f"http://127.0.0.1:{server.server_port}/v1", SAM_TEST_API_KEY="sensitive-test-key", SAM_TEST_TIMEOUT="0.08" if mode == "trickle" else "5")
                run = subprocess.run([str(ROOT / "scripts/probe.sh"), "--report", str(report)], env=env, capture_output=True, text=True)
                output = report.read_text()
                self.assertNotIn("sensitive-test-key", output + run.stdout + run.stderr)
                self.assertNotIn("secret-http-error-body", output + run.stdout + run.stderr)
                return run, json.loads(output), Handler.seen_models[:]
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_cli_live_loopback_and_private_report(self):
        run, report, models = self.exercise("valid")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(report["result"], "pass")
        self.assertEqual(report["sam_validation"], "not-run")
        self.assertEqual(models, ["test/model"] * 3)

    def test_http_error_cannot_pass(self):
        run, report, _ = self.exercise("http-error")
        self.assertEqual(run.returncode, 1)
        self.assertEqual(report["result"], "fail")

    def test_trickled_unfinished_sse_line_cannot_evade_budget(self):
        run, report, _ = self.exercise("trickle")
        self.assertEqual(run.returncode, 1)
        self.assertEqual([c["status"] for c in report["checks"]], ["pass", "fail", "pass"])
        self.assertIn("time budget", report["checks"][1]["detail"])

    def test_redirect_is_not_followed(self):
        run, report, models = self.exercise("redirect")
        self.assertEqual(run.returncode, 1)
        self.assertEqual(len(models), 2)  # H1 and H2 only; H3 cannot run.
        self.assertTrue(all(r["status"] == "fail" for r in report["checks"]))


class TraceTests(unittest.TestCase):
    def trace(self):
        return {"schema_version": 1, "evidence_origin": "live-sam", "sam_runtime": "test",
                "sam_version": "test", "adapter_version": "test", "model_revision": "test", "server_image_digest": "test",
                "run_id": "synthetic", "source_trace_sha256": "a" * 64,
                "events": [
                    {"kind": "tool_call", "turn": 0, "call_id": "a", "name": "lookup_order", "arguments": {"order_id": "ORD-1001"}},
                    {"kind": "tool_result", "call_id": "a", "result": {"warehouse": "random-opaque-code"}},
                    {"kind": "tool_call", "turn": 1, "call_id": "b", "name": "get_shipping_estimate", "arguments": {"warehouse": "random-opaque-code", "destination": "Copenhagen"}},
                    {"kind": "tool_result", "call_id": "b", "result": {"warehouse": "random-opaque-code", "destination": "Copenhagen", "days": 1, "cost_eur": 4.90}},
                    {"kind": "final_answer", "text": "1 day; EUR 4.90"}]}

    def test_observed_dependency_passes(self):
        self.assertTrue(trace_check.validate(self.trace(), "two-tool-dependency"))

    def test_wrong_dependency_and_missing_duration_fail(self):
        for mutation in ("warehouse", "duration", "order", "id", "origin"):
            trace = self.trace()
            if mutation == "warehouse": trace["events"][2]["arguments"]["warehouse"] = "guessed"
            if mutation == "duration": trace["events"][-1]["text"] = "EUR 4.90"
            if mutation == "order": trace["events"][1], trace["events"][2] = trace["events"][2], trace["events"][1]
            if mutation == "id": trace["events"][3]["call_id"] = "missing"
            if mutation == "origin": trace["evidence_origin"] = "mock-llm"
            with self.subTest(mutation=mutation), self.assertRaises(trace_check.InvalidTrace):
                trace_check.validate(trace, "two-tool-dependency")

    def test_parallel_must_share_turn_and_precede_results(self):
        trace = self.trace()
        trace["events"] = [
            {"kind": "tool_call", "turn": 0, "call_id": "a", "name": "lookup_order", "arguments": {"order_id": "ORD-1001"}},
            {"kind": "tool_call", "turn": 0, "call_id": "b", "name": "lookup_order", "arguments": {"order_id": "ORD-1002"}},
            {"kind": "tool_result", "call_id": "b", "result": {"item": "dock"}},
            {"kind": "tool_result", "call_id": "a", "result": {"item": "monitor"}},
            {"kind": "final_answer", "text": "monitor and dock"}]
        self.assertTrue(trace_check.validate(trace, "parallel-tools"))
        trace["events"][1]["turn"] = 1
        with self.assertRaises(trace_check.InvalidTrace): trace_check.validate(trace, "parallel-tools")

    def test_forced_mode_requires_captured_request_setting(self):
        trace = self.trace()
        trace["events"] = [
            {"kind": "tool_call", "turn": 0, "call_id": "a", "name": "lookup_order", "arguments": {"order_id": "ORD-1002"}},
            {"kind": "tool_result", "call_id": "a", "result": {"item": "dock"}},
            {"kind": "final_answer", "text": "dock"}]
        with self.assertRaises(trace_check.InvalidTrace): trace_check.validate(trace, "forced-tool")
        trace["request_tool_choice"] = "required"
        self.assertTrue(trace_check.validate(trace, "forced-tool"))

    def test_no_trace_is_incomplete(self):
        result = subprocess.run([str(ROOT / "scripts/run-sam-scenario.sh")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("INCOMPLETE", result.stdout)

    def test_source_hash_is_verified(self):
        with tempfile.TemporaryDirectory() as temp:
            source = pathlib.Path(temp) / "source.json"
            source.write_text('{"synthetic-test":true}')
            trace = self.trace()
            trace["source_trace_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
            normalized = pathlib.Path(temp) / "normalized.json"
            normalized.write_text(json.dumps(trace))
            command = [str(ROOT / "scripts/run-sam-scenario.sh"), "--trace", str(normalized), "--source-trace", str(source)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout)
            source.write_text('{"changed":true}')
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)


if __name__ == "__main__":
    unittest.main()
