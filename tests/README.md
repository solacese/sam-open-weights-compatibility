# Validation harness

Two levels of proof that a model works with Solace Agent Mesh. Run them in order - the probe is cheap and needs no SAM install; the scenario is the real thing.

## Level 1 - endpoint probe (no SAM)

`../scripts/probe.sh` hits your OpenAI-compatible endpoint directly with curl + jq and checks the three hard gates:

- **H1** - a non-streaming request with a tool returns a `tool_calls` finish reason with well-formed JSON args.
- **H2** - the same request in streaming mode emits incremental `tool_calls` deltas that reassemble into valid JSON.
- **H3** - a follow-up turn carrying a `tool` role message is accepted and produces a final answer.

```bash
export SAM_TEST_MODEL="openai/Qwen/Qwen2.5-32B-Instruct"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
export SAM_TEST_API_KEY="sk-noop"
../scripts/probe.sh
```

A model that fails any hard gate here will not work in SAM - stop and fix serving (usually a missing `--enable-auto-tool-choice` / wrong `--tool-call-parser`).

## Level 2 - live SAM agent scenario

`../scripts/run-sam-scenario.sh` runs a real SAM agent (`configs/agent.yaml`) wired to two dependent mock tools (`tools/validation_tools.py`). The agent must:

1. call `lookup_order(order_id)` → get a warehouse code,
2. call `get_shipping_estimate(warehouse, destination)` **using the code from step 1**,
3. answer with the estimate.

Step 2 is the discriminator: a model that fakes tool calling cannot round-trip the warehouse code, so the second call's `warehouse` argument will be wrong or missing. The mock tool data is deterministic, so the assertions are exact.

```bash
../scripts/run-sam-scenario.sh two-tool-dependency   # H1+H2+H3 end-to-end
../scripts/run-sam-scenario.sh forced-tool            # S1 tool_choice: required
../scripts/run-sam-scenario.sh parallel-tools         # N1 parallel tool calls
```

## Why the SAM integration harness isn't used here

The declarative harness in the SAM repo (`test/integration/scenarios/*.yaml`) **mocks the LLM** via `static_response`. That's the right tool for testing SAM's plumbing, but it can't tell you whether a *real* model calls tools correctly - the mock always does. These configs run a live model instead.

## Layout

```
configs/
  model.yaml     - SAM model: block, templated on SAM_TEST_* env vars
  agent.yaml     - ModelValidationAgent: the live agent under test
tools/
  validation_tools.py  - two dependent mock tools + JSON-schema mirror
scenarios/
  two-tool-dependency.yaml  - the core behavioral spec (assert order + arg round-trip)
  forced-tool.yaml          - tool_choice: required
  parallel-tools.yaml       - two independent calls in one turn
```
