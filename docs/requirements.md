# Compatibility requirements

Compatibility belongs to a **complete deployment tuple**: SAM runtime/version + adapter + gateway + serving engine + model revision + tokenizer/template + reasoning parser + quantization + hardware + request settings. The same checkpoint can pass on one tuple and fail on another.

## Protocol and behavioral gates

| Gate | Required behavior | Evidence to capture |
|---|---|---|
| H1 Native tool calls | Return structured `tool_calls`, nonempty call IDs, correct function name and JSON arguments | Exact schema validation, no text-only pseudo-calls |
| H2 Streaming, when enabled | Reassemble deltas by choice and tool index; preserve IDs, names, argument fragments and termination | Chunked SSE, multiple calls, usage-only chunks, interruptions |
| H3 Tool results | Associate each `tool_call_id` with its assistant call and use returned data in the next decision | Dependent two-tool task with an unpredictable intermediate result |
| S1 Tool choice, when used | Honor `auto`, `none`, `required`, and named choice as configured | Separate tests for each mode; a forced-call pass does not prove auto selection |
| S2 Context and output | Fit system instructions, tools, history, retrieval, results and output/reasoning budget | Overflow behavior and meaningful task success at configured limits |
| S3 Argument fidelity | Correct types, enums, nested values, escaping, required fields and extra-field policy | Validate with the application's schema; never execute unvalidated JSON |
| N1 Parallel calls, when used | Unique IDs, independent arguments and correctly associated results | Interleaved indices and out-of-order result completion |
| N2 Reasoning behavior | Preserve or clear reasoning history as required by the checkpoint and runtime | Reasoning on/off/effort tests; avoid discarding fields required for continued tool use |

H1 and H3 are central to tool-using agents. H2 is a gate for a streaming deployment, not a universal claim that every SAM configuration requires streaming. Forced tool choice becomes a hard requirement if the application uses it. Feature importance follows the actual agent configuration.

## Runtime distinctions

Go SAM's model configuration maps provider prefixes through Bifrost. Python SAM wraps LiteLLM and ADK. Their configuration surfaces and streaming behavior must be checked separately. In the checked Python source, `supports_streaming` defaults to false and describes A2A streaming; do not infer model protocol behavior from that flag alone. [Pinned source map](methodology.md).

The `openai/` prefix chooses a protocol. For example, `openai/Qwen/Qwen3.6-35B-A3B` sends `Qwen/Qwen3.6-35B-A3B` to your endpoint. A gateway alias such as `enterprise-orchestrator` can replace the checkpoint name. An OpenAI-compatible `/chat/completions` route does not imply Responses API compatibility, strict JSON Schema coverage, vision support or equivalent cancellation and usage accounting.

## Production qualification extends beyond protocol

- The task must reach the correct business outcome within its latency, token and cost budget.
- Tools enforce identity, authorization, argument validation and idempotency outside the model.
- The inference boundary enforces tenant isolation, request limits, privacy and outbound policy.
- The service must survive overload, replica/node loss, model load failure and rollback.

A missing parser in one engine is a limitation of that serving path, not proof that a model can never be adapted. Conversely, a parser entry or a leaderboard submission is not an observed compatibility pass.
