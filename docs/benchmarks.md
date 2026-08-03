# Benchmarks: how these models rank on tool calling

The one capability SAM depends on is reliable tool calling, so the benchmark that matters most here is the **Berkeley Function-Calling Leaderboard (BFCL)** - it measures exactly the behavior SAM exercises (single and multi-turn function calling, argument fidelity, and the ability to decide when *not* to call a tool). General-knowledge scores (MMLU, etc.) are secondary; a model that scores high on MMLU but poorly on BFCL is a bad SAM fit.

> Numbers below are the published figures as of the date noted in the table. Leaderboards move; treat these as a ranking signal, not a contract. The [validation harness](validation.md) is the source of truth for your stack.

## Why BFCL over general benchmarks

- SAM's agent loop is: model emits a `tool_calls` finish reason -> SAM executes -> feeds results back -> model continues. BFCL's "multi-turn" and "live" categories measure precisely this.
- BFCL penalizes the two failures that break SAM agents in practice: malformed JSON arguments (breaks execution) and hallucinated / unnecessary tool calls (breaks agent logic).
- A high general-reasoning score does not imply good tool calling. This is why some strong chat models (Gemma 2, Phi-4, Yi) are poor SAM fits despite good MMLU.

<!-- BENCHMARK_TABLE_START -->

The verdict per model, cross-checked against all three sources. "BFCL V4" is the overall accuracy on the live [Berkeley Function-Calling Leaderboard V4](https://gorilla.cs.berkeley.edu/leaderboard.html), observed 2026-07-31 (`(FC)` = function-calling variant, `(P)` = prompt variant, highest shown; `n/a` = not on the current board, which prunes older checkpoints). "BFCL tier" is whether the model appears in BFCL's native **Function-Calling** list or only its **Prompt** list (prompt-only = no native FC). "vLLM parser" is the `--tool-call-parser` value, or `none` if vLLM ships no parser for it. "HF `tool` role" is whether the model's chat template defines the tool-calling turns SAM needs (H3).

| Model | BFCL V4 | BFCL tier | vLLM parser | HF `tool` role | SAM verdict |
|---|---|---|---|---|---|
| Llama 3.3 70B Instruct | 31.9 (FC) | Function Calling | `llama3_json` | yes | excellent |
| Qwen2.5 72B Instruct | n/a | Function Calling | `hermes` | yes | excellent |
| Qwen2.5 32B Instruct | n/a | Function Calling | `hermes` | yes | excellent |
| Qwen3 32B | 48.71 (FC) | Function Calling | `hermes` | yes | excellent |
| Mistral Large 2 (2411) | 38.37 (FC) | Function Calling | `mistral` | yes | excellent |
| Llama 3.1 405B Instruct | n/a | Function Calling | `llama3_json` | yes | excellent |
| Llama 3.1 70B Instruct | n/a | Function Calling | `llama3_json` | yes | excellent |
| DeepSeek-V3.1 | n/a | Function Calling | `deepseek_v31` | yes | very-good |
| GLM-4.6 | 72.38 (FC) | Function Calling | `glm45` | yes | very-good |
| gpt-oss 120b | n/a | Function Calling | `openai` | yes (harmony) | very-good |
| Kimi-K2 Instruct | 59.06 (FC) | Function Calling | `kimi_k2` | yes | very-good |
| Command A (03-2025) | 46.49 (FC) | Function Calling | `cohere_command3` | yes | very-good |
| Qwen2.5 14B Instruct | n/a | Function Calling | `hermes` | yes | very-good |
| Mixtral 8x22B Instruct | n/a | not listed | `mistral` | yes | good |
| Mistral Small 3 (24B) | n/a | Function Calling | `mistral` | yes | very-good |
| Qwen2.5 7B Instruct | n/a | Function Calling | `hermes` | yes | good |
| Qwen2.5-Coder 32B | n/a | Function Calling | `hermes` | yes | very-good |
| gpt-oss 20b | n/a | Function Calling | `openai` | yes (harmony) | good |
| Mistral NeMo 12B | 27.63 (FC) | Function Calling | `mistral` | yes | good |
| Llama 3.1 8B Instruct | 25.83 (P) | Function Calling | `llama3_json` | yes | good |
| DeepSeek-R1 (0528) | n/a | Prompt (base R1) | `deepseek_v3` | conditional | validate-first |
| Command R+ (legacy) | n/a | Function Calling | none | yes | validate-first |
| Gemma 2 27B Instruct | n/a | Prompt only | none | no | unsupported |
| Phi-4 (14B) | 28.79 (P) | Prompt only | none | no | unsupported |
| Yi-1.5 34B Chat | n/a | not in FC tier | none | no | unsupported |

A note on the scores: BFCL V4 (observed 2026-07-31) has pruned most pre-2025 checkpoints, so 16 of these 25 models are simply absent from the current board (`n/a`) rather than scoring poorly. Where a live number exists, GLM-4.6 (72.38), Kimi-K2 (59.06), and Qwen3 32B (48.71) lead this set. Absolute values are low by MMLU standards because BFCL is deliberately hard (multi-turn, multi-step, and "do not call a tool" cases); treat the number as a relative ranking signal among models that *have* one, and the tier/parser/template columns as the pass/fail on whether SAM can drive the model at all.

Reading the table:

- **Function Calling + a real vLLM parser + a `tool` role** = the model does native tool calling and SAM can drive it. These are `excellent`/`very-good`/`good` (the last for smaller models where JSON-arg fidelity, S3, wobbles under load or quant).
- **Command R+ (legacy)** is on the BFCL FC tier but current vLLM ships no parser for it, so on a stock vLLM serve tool calling will not fire; that mismatch is exactly why it is `validate-first`, not `very-good`. Command A (#12) supersedes it and has the `cohere_command3` parser.
- **DeepSeek-R1** is only on the BFCL Prompt tier for the base model; the **0528** revision plus the R1 chat template is what makes native FC conditional-but-possible, hence `validate-first`.
- **Gemma 2, Phi-4, Yi-1.5** have no parser, no `tool` role, and sit in the Prompt tier (or are absent from the FC tier). No amount of prompting makes them pass H1. Only `google/functiongemma-270m-it` (a separate, tiny FC-tuned Gemma) has function calling.

<!-- BENCHMARK_TABLE_END -->

## Sources

- Berkeley Function-Calling Leaderboard (BFCL): https://gorilla.cs.berkeley.edu/leaderboard.html
- vLLM tool-calling support matrix (authoritative for which models have a working parser): https://docs.vllm.ai/en/latest/features/tool_calling.html
- Individual model cards on Hugging Face (linked from each `models/cards/*.md`).
