#!/usr/bin/env python3
"""Assert scenario evidence exported from a real SAM trace. Does not launch SAM."""
import argparse
import hashlib
import json
import pathlib
import re


class InvalidTrace(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise InvalidTrace(reason)


def validate(trace, scenario):
    require(trace.get("schema_version") == 1, "unsupported trace schema")
    require(trace.get("evidence_origin") == "live-sam", "trace is not declared live SAM evidence")
    for field in ("sam_runtime", "sam_version", "model_revision", "server_image_digest", "adapter_version", "run_id"):
        require(isinstance(trace.get(field), str) and trace[field].strip(), f"missing provenance: {field}")
    require(bool(re.fullmatch(r"[0-9a-f]{64}", trace.get("source_trace_sha256", ""))), "missing source trace SHA-256")
    events = trace.get("events")
    require(isinstance(events, list) and events, "missing events")
    calls, results, finals = [], {}, []
    ids = set()
    call_positions = {}
    result_positions = {}
    for position, event in enumerate(events):
        require(isinstance(event, dict), "invalid event")
        kind = event.get("kind")
        require(not finals, "events after final answer")
        if kind == "tool_call":
            cid = event.get("call_id")
            require(isinstance(cid, str) and cid and cid not in ids, "missing/duplicate call ID")
            require(isinstance(event.get("arguments"), dict), "arguments must be a decoded object")
            require(isinstance(event.get("turn"), int) and event["turn"] >= 0, "missing turn index")
            ids.add(cid)
            calls.append(event)
            call_positions[cid] = position
        elif kind == "tool_result":
            cid = event.get("call_id")
            require(cid in ids and cid not in results, "unmatched/duplicate result")
            require(isinstance(event.get("result"), dict) and "error" not in event["result"], "failed/malformed tool result")
            results[cid] = event["result"]
            result_positions[cid] = position
        elif kind == "final_answer":
            require(isinstance(event.get("text"), str) and event["text"].strip(), "empty final answer")
            finals.append(event["text"])
        else:
            raise InvalidTrace("unknown event kind")
    require(len(finals) == 1 and ids == results.keys(), "missing final answer or tool results")
    final = finals[0]
    if scenario == "two-tool-dependency":
        require([c.get("name") for c in calls] == ["lookup_order", "get_shipping_estimate"], "wrong tool sequence")
        first, second = calls
        require(first["arguments"] == {"order_id": "ORD-1001"}, "wrong order lookup")
        warehouse = results[first["call_id"]].get("warehouse")
        require(isinstance(warehouse, str) and warehouse, "missing returned warehouse")
        require(result_positions[first["call_id"]] < call_positions[second["call_id"]], "second call preceded first result")
        require(second["arguments"] == {"warehouse": warehouse, "destination": "Copenhagen"}, "dependency argument mismatch")
        shipping = results[second["call_id"]]
        require(shipping.get("warehouse") == warehouse and shipping.get("destination") == "Copenhagen", "shipping result mismatch")
        require(shipping.get("days") == 1 and shipping.get("cost_eur") == 4.90, "unexpected shipping result")
        require(("4.90" in final or "4,90" in final) and ("1 day" in final or "1 business day" in final), "final answer missing cost or duration")
    elif scenario == "forced-tool":
        require(trace.get("request_tool_choice") in ("required", "lookup_order"), "no captured forced-tool request setting")
        require(len(calls) == 1 and calls[0].get("name") == "lookup_order", "forced tool not called")
        require(calls[0]["arguments"] == {"order_id": "ORD-1002"}, "wrong forced-tool order")
        item = results[calls[0]["call_id"]].get("item")
        require(isinstance(item, str) and item and item in final, "final answer missing observed item")
    else:
        require(len(calls) == 2 and all(c.get("name") == "lookup_order" for c in calls), "expected two lookups")
        require({c["arguments"].get("order_id") for c in calls} == {"ORD-1001", "ORD-1002"}, "wrong parallel orders")
        require(calls[0]["turn"] == calls[1]["turn"], "serial calls do not demonstrate parallel tools")
        require(max(call_positions.values()) < min(result_positions.values()), "calls not emitted before results")
        for call in calls:
            item = results[call["call_id"]].get("item")
            require(isinstance(item, str) and item and item in final, "final answer missing observed item")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", nargs="?", default="two-tool-dependency", choices=["two-tool-dependency", "forced-tool", "parallel-tools"])
    parser.add_argument("--trace", type=pathlib.Path)
    parser.add_argument("--source-trace", type=pathlib.Path, help="original runtime export whose hash must match")
    args = parser.parse_args()
    if not args.trace or not args.source_trace:
        print("INCOMPLETE: provide --trace normalized.json and --source-trace original-export.json.")
        print("Run the live SAM workflow first, export its real tool trace, and normalize it as documented in docs/validation.md.")
        print("This checker does not launch SAM or claim a pass from a CLI exit code.")
        return 2
    try:
        trace = json.loads(args.trace.read_text())
        require(isinstance(trace, dict), "trace must be an object")
        actual_hash = hashlib.sha256(args.source_trace.read_bytes()).hexdigest()
        require(trace.get("source_trace_sha256") == actual_hash, "source trace hash mismatch")
        validate(trace, args.scenario)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        # Trace content can contain secrets; print only controlled validation messages.
        print("FAIL: " + (str(exc) if isinstance(exc, InvalidTrace) else "unreadable or malformed trace"))
        return 1
    print(f"PASS: {args.scenario} assertions on supplied SAM trace. Source hash matched; provenance requires reviewer verification.")
    print("This does not certify production readiness or independently authenticate trace origin.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
