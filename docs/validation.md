# Validate a model and deployment bundle

There are three distinct activities: an executable endpoint smoke probe, assertions on a real exported SAM trace, and broader enterprise qualification. None substitutes for the next.

## 1. Endpoint smoke probe

Run from the repository root with Python 3.10+:

```bash
export SAM_TEST_MODEL='openai/sam-candidate'
export SAM_TEST_API_BASE='http://127.0.0.1:8000/v1'
# Set SAM_TEST_API_KEY through your secret environment when required.
./scripts/probe.sh --report probe-result.json
```

| Check | Assertion |
|---|---|
| H1 | One native `get_weather` call, nonempty ID, `tool_calls` finish reason, exact JSON city argument |
| H2 | Valid SSE, choice/tool indices, name/argument fragments, unique IDs and complete termination; reconstructed call passes H1 argument checks |
| H3 | Continue from the H1 assistant call and a linked tool result containing an unpredictable receipt; reproduce receipt AND temperature, finish normally and make no extra call |

The random receipt reduces false passes from memorized weather answers. This is still a small behavioral sample, not proof of general tool competence. H2 checks one streamed tool call; parser regression tests also cover interleaved indices, but live parallel capability requires a separate test.

Exit codes: **0** all smoke checks passed; **1** one or more failed; **2** invalid/missing configuration. HTTP, TLS, malformed response and incomplete stream failures cannot become passes. Network requests have time/response-size limits, TLS verification stays enabled, and redirects are rejected. Reports exclude credentials, endpoint URLs and response bodies. The model ID is recorded; handle reports according to your information policy.

| Environment variable | Meaning |
|---|---|
| `SAM_TEST_MODEL` | SAM-style model name; only a leading `openai/` protocol prefix is removed |
| `SAM_TEST_BARE_MODEL` | Optional exact endpoint ID override, useful for another adapter prefix |
| `SAM_TEST_API_BASE` | Base ending in `/v1` or the route your endpoint uses before `/chat/completions` |
| `SAM_TEST_API_KEY` | Optional bearer credential; no default fake key is sent |
| `SAM_TEST_TIMEOUT` | Request budget in seconds, default 120 |
| `SAM_TEST_EXTRA_BODY` | JSON generation settings such as `max_tokens`, reasoning or template options; cannot override the probe's model/tools/messages/stream/choice contract |

For gpt-oss hub names, `SAM_TEST_MODEL='openai/openai/gpt-oss-120b'` correctly leaves endpoint ID `openai/gpt-oss-120b`. Prefer a stable gateway alias. If a model exhausts its reasoning budget, qualify a suitable higher limit rather than mislabeling the model unsupported.

Run through the production gateway route as well as the isolated backend test route. A backend pass does not qualify a gateway's SSE and tool-field handling.

## 2. Real SAM scenarios

Use your installed SAM runtime and a working project with broker, gateway, identities and model configuration. The fragments in `tests/configs/` illustrate tool registration and **must be merged into that project**. They are not a standalone bootable environment. `tests/tools/validation_tools.py` contains synthetic business tools; the model must be live, without a static/mocked LLM response.

Submit the prompt in the chosen `tests/scenarios/*.yaml`. Export the actual runtime trace, including tool calls and results. On the inspected Python CLI, `sam task run --help` exposes `--config`, `--agent` and `--output-dir`; it does **not** expose the old runner's assumed `--format json`. The Go runtime and other releases can differ. Verify the command and trace format on your installed version.

Normalize the original trace into this JSON contract, preserving event order and observed values:

```json
{
  "schema_version": 1,
  "evidence_origin": "live-sam",
  "sam_runtime": "python-or-go",
  "sam_version": "actual-release-or-commit",
  "adapter_version": "actual-adapter-version",
  "model_revision": "actual-weight-revision",
  "server_image_digest": "sha256:actual-image-digest",
  "run_id": "actual-task-id",
  "source_trace_sha256": "64-lowercase-hex-digits-of-original-export",
  "events": [
    {"kind":"tool_call","turn":0,"call_id":"a","name":"lookup_order","arguments":{"order_id":"ORD-1001"}},
    {"kind":"tool_result","call_id":"a","result":{"warehouse":"observed-opaque-code"}},
    {"kind":"tool_call","turn":1,"call_id":"b","name":"get_shipping_estimate","arguments":{"warehouse":"observed-opaque-code","destination":"Copenhagen"}},
    {"kind":"tool_result","call_id":"b","result":{"warehouse":"observed-opaque-code","destination":"Copenhagen","days":1,"cost_eur":4.90}},
    {"kind":"final_answer","text":"Shipping takes 1 day and costs EUR 4.90."}
  ]
}
```

This documentation example is not executable evidence. Do not manufacture or edit event values to satisfy the checker. A runtime-specific exporter/normalizer is intentionally required; this repository does not claim a universal live trace adapter. Verify normalization against the original trace during review. A hash detects mismatched files; it does not authenticate the origin or semantic accuracy of a supplied trace.

```bash
./scripts/run-sam-scenario.sh two-tool-dependency \
  --trace normalized.json --source-trace original-export.json
```

The checker verifies the source hash, required provenance fields, matched call IDs/results, sequence, use of the **observed** warehouse and both shipping cost and duration in the final answer. Tool fixtures randomize warehouse codes per process startup. A supplied trace without a verifiable original export is incomplete.

`forced-tool` additionally requires a captured `request_tool_choice` value of `required` or `lookup_order`; a prompt telling the model to use tools does not prove forced choice. `parallel-tools` requires both lookups in the same assistant turn before either result, unique IDs and both observed items in the final answer. Sequential correctness does not demonstrate parallel calling.

The script exits **2 / INCOMPLETE** if required trace inputs are absent, **1 / FAIL** for failed assertions or malformed evidence, and **0 / PASS** only for assertions on the supplied evidence. It does not launch SAM and does not assert that H2 was exercised; retain the endpoint streaming result and the runtime request/stream configuration separately.

## 3. Promotion evidence

Copy `tests/results/qualification-template.json` into your restricted evidence store. Attach endpoint reports, original/normalized SAM traces, held-out task results, artifact hashes, limits, load/failure tests and approvals. Never put credentials or confidential traces into this public repository.

| Evidence | What it establishes |
|---|---|
| Endpoint PASS only | This small protocol sample passed on the endpoint |
| Endpoint + supplied SAM trace PASS | Smoke protocol checks and the supplied runtime scenario assertions passed |
| Held-out workload, security, load and recovery gates accepted | Readiness for the explicitly tested workload/envelope, subject to owner approval |

A pass on a different quantization, template, gateway, reasoning setting or runtime version must not be copied into a new deployment's validation record.
