# Benchmarks: how these models rank on tool calling

The one capability SAM depends on is reliable tool calling, so the benchmark that matters most here is the **Berkeley Function-Calling Leaderboard (BFCL)** - it measures exactly the behavior SAM exercises (single and multi-turn function calling, argument fidelity, and the ability to decide when *not* to call a tool). General-knowledge scores (MMLU, etc.) are secondary; a model that scores high on MMLU but poorly on BFCL is a bad SAM fit.

> Numbers below are the published figures as of the date noted in the table. Leaderboards move; treat these as a ranking signal, not a contract. The [validation harness](validation.md) is the source of truth for your stack.

## Why BFCL over general benchmarks

- SAM's agent loop is: model emits a `tool_calls` finish reason -> SAM executes -> feeds results back -> model continues. BFCL's "multi-turn" and "live" categories measure precisely this.
- BFCL penalizes the two failures that break SAM agents in practice: malformed JSON arguments (breaks execution) and hallucinated / unnecessary tool calls (breaks agent logic).
- A high general-reasoning score does not imply good tool calling. This is why some strong chat models (Gemma 2, Phi-4, Yi) are poor SAM fits despite good MMLU.

<!-- BENCHMARK_TABLE_START -->

The verdict per model, cross-checked against all three sources, **sorted by BFCL overall accuracy (highest first)**. "BFCL" is the overall accuracy: `(V4)` = the live [Berkeley Function-Calling Leaderboard V4](https://gorilla.cs.berkeley.edu/leaderboard.html) (observed 2026-07-31); `(V3)` = the archived V3 `data_overall.csv` snapshot (2025-03, [Wayback](https://web.archive.org/web/20250317113918id_/https://gorilla.cs.berkeley.edu/data_overall.csv)) for the checkpoints V4 pruned. `(FC)` = function-calling variant, `(P)` = prompt variant (highest shown). `n/a` = never submitted to BFCL in any version. "BFCL tier" is whether the model appears in BFCL's native **Function-Calling** list or only its **Prompt** list (prompt-only = no native FC). "vLLM parser" is the `--tool-call-parser` value, or `none` if vLLM ships no parser for it. "HF `tool` role" is whether the model's chat template defines the tool-calling turns SAM needs (H3).

**The score order is not the SAM-fitness order.** V3 and V4 numbers are not directly comparable (BFCL re-scores between versions - R1-0528 alone moved 63.79 to 48.97 across two 2025 snapshots), and a high score does not imply SAM can drive the model (Gemma 2 scores 52.21 in *prompt* mode yet fails SAM's first hard gate). The **SAM verdict** column is the fitness signal; the score is supporting evidence. For the SAM-fitness ranking use [`shortlist.md`](shortlist.md).

| Model | BFCL | BFCL tier | vLLM parser | HF `tool` role | SAM verdict |
|---|---|---|---|---|---|
| GLM-4.6 | 72.38 (FC, V4) | Function Calling | `glm45` | yes | very-good |
| DeepSeek-R1 (0528) | 63.79 (FC, V4) | Prompt (base R1) | `deepseek_v3` | conditional | validate-first |
| Qwen2.5 72B Instruct | 61.31 (P, V3) | Function Calling | `hermes` | yes | excellent |
| Qwen2.5 32B Instruct | 59.67 (P, V3) | Function Calling | `hermes` | yes | excellent |
| Kimi-K2 Instruct | 59.06 (FC, V4) | Function Calling | `kimi_k2` | yes | very-good |
| Qwen2.5 14B Instruct | 57.68 (P, V3) | Function Calling | `hermes` | yes | very-good |
| DeepSeek-V3.1 | 57.23 (FC, V3) | Function Calling | `deepseek_v31` | yes | very-good |
| Qwen2.5 7B Instruct | 56.70 (FC, V3) | Function Calling | `hermes` | yes | good |
| Llama 3.1 70B Instruct | 54.19 (P, V3) | Function Calling | `llama3_json` | yes | excellent |
| Gemma 2 27B Instruct | 52.21 (P, V3) | Prompt only | none | no | unsupported |
| Mixtral 8x22B Instruct | 50.36 (P, V3) | not listed | `mistral` | yes | good |
| Command R+ (legacy) | 49.35 (FC, V3) | Function Calling | none | yes | validate-first |
| Qwen3 32B | 48.71 (FC, V4) | Function Calling | `hermes` | yes | excellent |
| Command A (03-2025) | 46.49 (FC, V4) | Function Calling | `cohere_command3` | yes | very-good |
| Mistral Large 2 (2411) | 38.37 (FC, V4) | Function Calling | `mistral` | yes | excellent |
| Llama 3.3 70B Instruct | 31.9 (FC, V4) | Function Calling | `llama3_json` | yes | excellent |
| Phi-4 (14B) | 28.79 (P, V4) | Prompt only | none | no | unsupported |
| Mistral NeMo 12B | 27.63 (FC, V4) | Function Calling | `mistral` | yes | good |
| Llama 3.1 8B Instruct | 25.83 (P, V4) | Function Calling | `llama3_json` | yes | good |
| Llama 3.1 405B Instruct | n/a | Function Calling | `llama3_json` | yes | excellent |
| gpt-oss 120b | n/a | Function Calling | `openai` | yes (harmony) | very-good |
| Mistral Small 3 (24B) | n/a | Function Calling | `mistral` | yes | very-good |
| Qwen2.5-Coder 32B | n/a | Function Calling | `hermes` | yes | very-good |
| gpt-oss 20b | n/a | Function Calling | `openai` | yes (harmony) | good |
| Yi-1.5 34B Chat | n/a | not in FC tier | none | no | unsupported |

A note on the scores: 19 of these 25 models have a BFCL number once you include the archived V3 board (2025-03) for the checkpoints V4 pruned; the remaining six were never submitted to BFCL in any version (`n/a`), not scored poorly. Absolute values are low by MMLU standards because BFCL is deliberately hard (multi-turn, multi-step, and "do not call a tool" cases); treat the number as a relative signal among models on the *same* board version, and the tier/parser/template columns as the pass/fail on whether SAM can drive the model at all. The DeepSeek-V3.1 row carries the original DeepSeek-V3 score (BFCL never listed a distinct V3.1).

Reading the table:

- **Function Calling + a real vLLM parser + a `tool` role** = the model does native tool calling and SAM can drive it. These are `excellent`/`very-good`/`good` (the last for smaller models where JSON-arg fidelity, S3, wobbles under load or quant).
- **Score rank ≠ verdict.** DeepSeek-R1-0528 is #2 by score but `validate-first`; Gemma 2 is #10 by score but `unsupported`. Both illustrate why the verdict column, not the number, decides SAM fitness.
- **Command R+ (legacy)** is on the BFCL FC tier but current vLLM ships no parser for it, so on a stock vLLM serve tool calling will not fire; that mismatch is exactly why it is `validate-first`, not `very-good`. Command A supersedes it and has the `cohere_command3` parser.
- **DeepSeek-R1** is only on the BFCL Prompt tier for the base model; the **0528** revision plus the R1 chat template is what makes native FC conditional-but-possible, hence `validate-first`.
- **Gemma 2, Phi-4, Yi-1.5** have no parser, no `tool` role, and sit in the Prompt tier (or are absent from the FC tier). No amount of prompting makes them pass H1. Their scores are prompt-mode pseudo-JSON, not the native `tool_calls` SAM's loop consumes. Only `google/functiongemma-270m-it` (a separate, tiny FC-tuned Gemma) has function calling.

<!-- BENCHMARK_TABLE_END -->

## Sources

- Berkeley Function-Calling Leaderboard (BFCL): https://gorilla.cs.berkeley.edu/leaderboard.html
- vLLM tool-calling support matrix (authoritative for which models have a working parser): https://docs.vllm.ai/en/latest/features/tool_calling.html
- Individual model cards on Hugging Face (linked from each `models/cards/*.md`).
