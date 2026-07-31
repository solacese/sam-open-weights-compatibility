# Benchmarks: how these models rank on tool calling

The one capability SAM depends on is reliable tool calling, so the benchmark that matters most here is the **Berkeley Function-Calling Leaderboard (BFCL)** - it measures exactly the behavior SAM exercises (single and multi-turn function calling, argument fidelity, and the ability to decide when *not* to call a tool). General-knowledge scores (MMLU, etc.) are secondary; a model that scores high on MMLU but poorly on BFCL is a bad SAM fit.

> Numbers below are the published figures as of the date noted in the table. Leaderboards move; treat these as a ranking signal, not a contract. The [validation harness](validation.md) is the source of truth for your stack.

## Why BFCL over general benchmarks

- SAM's agent loop is: model emits a `tool_calls` finish reason -> SAM executes -> feeds results back -> model continues. BFCL's "multi-turn" and "live" categories measure precisely this.
- BFCL penalizes the two failures that break SAM agents in practice: malformed JSON arguments (breaks execution) and hallucinated / unnecessary tool calls (breaks agent logic).
- A high general-reasoning score does not imply good tool calling. This is why some strong chat models (Gemma 2, Phi-4, Yi) are poor SAM fits despite good MMLU.

<!-- BENCHMARK_TABLE_START -->

The verdict per model, cross-checked against all three sources. "BFCL tier" is whether the model appears in BFCL's native **Function-Calling** list or only its **Prompt** list (prompt-only = no native FC). "vLLM parser" is the `--tool-call-parser` value, or `none` if vLLM ships no parser for it. "HF `tool` role" is whether the model's chat template defines the tool-calling turns SAM needs (H3).

| Model | BFCL tier | vLLM parser | HF `tool` role | SAM verdict |
|---|---|---|---|---|
| Llama 3.3 70B Instruct | Function Calling | `llama3_json` | yes | excellent |
| Qwen2.5 72B Instruct | Function Calling | `hermes` | yes | excellent |
| Qwen2.5 32B Instruct | Function Calling | `hermes` | yes | excellent |
| Qwen3 32B | Function Calling | `hermes` | yes | excellent |
| Mistral Large 2 (2411) | Function Calling | `mistral` | yes | excellent |
| Llama 3.1 405B Instruct | Function Calling | `llama3_json` | yes | excellent |
| Llama 3.1 70B Instruct | Function Calling | `llama3_json` | yes | excellent |
| DeepSeek-V3.1 | Function Calling | `deepseek_v31` | yes | very-good |
| GLM-4.6 | Function Calling | `glm45` | yes | very-good |
| gpt-oss 120b | Function Calling | `openai` | yes (harmony) | very-good |
| Kimi-K2 Instruct | Function Calling | `kimi_k2` | yes | very-good |
| Command A (03-2025) | Function Calling | `cohere_command3` | yes | very-good |
| Qwen2.5 14B Instruct | Function Calling | `hermes` | yes | very-good |
| Mixtral 8x22B Instruct | not listed | `mistral` | yes | good |
| Mistral Small 3 (24B) | Function Calling | `mistral` | yes | very-good |
| Qwen2.5 7B Instruct | Function Calling | `hermes` | yes | good |
| Qwen2.5-Coder 32B | Function Calling | `hermes` | yes | very-good |
| gpt-oss 20b | Function Calling | `openai` | yes (harmony) | good |
| Mistral NeMo 12B | Function Calling | `mistral` | yes | good |
| Llama 3.1 8B Instruct | Function Calling | `llama3_json` | yes | good |
| DeepSeek-R1 (0528) | Prompt (base R1) | `deepseek_v3` | conditional | validate-first |
| Command R+ (legacy) | Function Calling | none | yes | validate-first |
| Gemma 2 27B Instruct | Prompt only | none | no | unsupported |
| Phi-4 (14B) | Prompt only | none | no | unsupported |
| Yi-1.5 34B Chat | not in FC tier | none | no | unsupported |

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
