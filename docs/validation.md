# Validating a Model

Grades in the [shortlist](shortlist.md) are starting points. This is how you get a definitive **yes/no** for a specific model, quant, and serving stack. Two levels:

1. **`probe.sh`** - talks straight to your OpenAI-compatible endpoint with `curl`. No SAM required. Checks the three hard gates in isolation. Fast, catches most failures.
2. **`run-sam-scenario.sh`** - runs a real SAM agent through a two-tool scenario. This is the ground truth: it exercises the actual agent loop, streaming reassembly, and multi-turn tool-result handling that a raw probe can't fully reproduce.

Always run `probe.sh` first (cheap), then confirm with the SAM scenario.

---

## Validate any model in 3 commands

```bash
# 1. Point at your endpoint (any OpenAI-compatible server)
export SAM_TEST_MODEL="openai/Qwen/Qwen2.5-32B-Instruct"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
export SAM_TEST_API_KEY="sk-noop"        # many local servers ignore this

# 2. Run the capability probe (no SAM required - pure OpenAI-compat check)
../scripts/probe.sh

# 3. Run the full SAM two-tool agent scenario (requires SAM installed)
../scripts/run-sam-scenario.sh
```

`probe.sh` checks the three hard gates directly against the endpoint. `run-sam-scenario.sh` runs a real SAM agent that must call tool A, then call tool B *using A's output* - the exact loop that separates real tool-callers from pretenders. The rest of this page explains each level and how to read the results.

---

## Prerequisites

- A model served behind an OpenAI-compatible API. See [serving.md](serving.md) to stand one up.
- `curl` and `jq` for the probe.
- SAM installed for the full scenario (`sam` on PATH). See the [SAM install docs](https://github.com/SolaceDev/solace-agent-mesh).

```bash
export SAM_TEST_MODEL="openai/Qwen/Qwen2.5-32B-Instruct"   # provider/model
export SAM_TEST_API_BASE="http://localhost:8000/v1"        # your endpoint
export SAM_TEST_API_KEY="sk-noop"                          # any value if server ignores it
```

---

## Level 1 - the endpoint probe

```bash
./scripts/probe.sh
```

It runs three checks and prints a PASS/FAIL per hard gate:

| Check | Gate | What it sends | Pass condition |
|---|---|---|---|
| **1. Tool call** | H1 | A `tools` array with `get_weather(city)` and a prompt that needs it | Response has `choices[0].message.tool_calls[0].function.name == "get_weather"` with JSON args containing a city |
| **2. Streaming tool call** | H2 | Same, with `"stream": true` | SSE chunks carry `delta.tool_calls[]`; concatenated `arguments` fragments parse as valid JSON |
| **3. Tool-result turn** | H3 | The assistant tool_call turn + a `tool` role result, asks for a final answer | Response *uses* the returned value (e.g. mentions the temperature) and does not re-call the tool or hallucinate |

A model that fails any of these is **not SAM-compatible** on this stack - fix the serving (tool parser, template, quant) or pick another model.

### Reading failures

- **No `tool_calls` at all** → missing/wrong `--tool-call-parser` (vLLM) or the model genuinely can't tool-call. Fails H1.
- **Tool call in non-stream but not stream** → server doesn't emit tool-call deltas while streaming. Fails H2 - a common vLLM/SGLang flag issue.
- **Malformed JSON in `arguments`** → quant too aggressive or template mismatch. Borderline S3; will cause dispatch errors in SAM.
- **Ignores the tool result / re-calls the tool** → chat template can't represent the `tool` turn. Fails H3.

---

## Level 2 - the SAM two-tool scenario

This is the real test. The scenario forces a **dependent** two-step tool chain: the agent must call `lookup_order`, then call `get_shipping_estimate` **using the warehouse code returned by the first call**. A model that fakes tool calling cannot pass this - it has no way to invent the correct warehouse code.

```bash
./scripts/run-sam-scenario.sh
```

Under the hood this:

1. Renders `tests/configs/model.yaml` and `tests/configs/agent.yaml` from your `SAM_TEST_*` env vars.
2. Starts SAM embedded with those configs.
3. Submits the scenario prompt from `tests/scenarios/two-tool-dependency.yaml`.
4. Asserts the agent called both tools **in order**, that the second call's `warehouse` argument matches the first call's returned value, and that the final answer contains the expected shipping figure.

### What each scenario proves

| Scenario file | Proves | Gate(s) |
|---|---|---|
| `two-tool-dependency.yaml` | Dependent multi-hop tool use - the core agent loop | H1, H2, H3, S3 |
| `forced-tool.yaml` | `tool_choice: required` is honored (mandatory call) | S1 |
| `parallel-tools.yaml` | Two independent tools in one turn, results ordered | N1 |

Run a specific scenario:

```bash
./scripts/run-sam-scenario.sh forced-tool
./scripts/run-sam-scenario.sh parallel-tools
```

---

## Interpreting the overall result

| probe.sh | SAM scenario | Verdict |
|---|---|---|
| All PASS | two-tool PASS | ✅ **Production-viable** on this stack. Run `forced-tool` + `parallel-tools` to grade S1/N1. |
| All PASS | two-tool FAIL | ⚠ Streaming/multi-turn issue the probe missed - check tool parser + template. Not yet viable. |
| H1 PASS, H2 FAIL | - | ❌ Streaming tool calls broken. Fix serving flags or don't stream (loses SAM's default UX). |
| H1 FAIL | - | ❌ Model/stack can't tool-call. Not compatible. |

## Recording results

Log outcomes in your own copy of `models/index.csv` (columns include `validated_stack` and `validated_date`) so your team has a stack-specific truth table, not just the generic grades. Example row convention:

```
Qwen2.5-32B-Instruct,openai,128000,Excellent,Apache-2.0,orchestrator,"vLLM 0.6.x, AWQ 4-bit, --tool-call-parser hermes","2026-07-31: probe PASS, two-tool PASS, forced-tool PASS"
```
