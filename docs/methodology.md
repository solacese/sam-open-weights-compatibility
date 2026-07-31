# Methodology — How These Conclusions Were Derived

This document exists so the requirements are auditable. Every claim in [requirements.md](requirements.md) traces to a specific place in the SAM codebase (`solace-agent-mesh-go`) or the official SAM documentation. Nothing here is inferred from a model vendor's marketing.

## Sources

1. **`internal/llm/client.go`** — the `llm.Client` interface and its request/response types. This is the contract the entire agent core programs against. It is the single most authoritative artifact: whatever the interface requires of a model, a model must provide.
2. **`internal/llm/bifrost.go`** — the Bifrost-backed implementation. Shows how SAM's abstract request maps to the wire (e.g. how `ToolChoice` becomes a Bifrost `ChatToolChoice`).
3. **`internal/agentcore/agent.go`** + `auto_continue.go` — the multi-turn tool-calling loop, streaming reassembly, and parallel-tool ordering.
4. **`internal/agentcore/structured/`** — the structured-output / forced-tool paths that rely on `tool_choice`.
5. **`internal/samapp/model.go`** — how model config YAML is parsed (`knownProviders`, `knownModelConfigKeys`, `nonCompletionKeys`), which defines exactly which config keys are honored.
6. **`internal/llm/modelinfo/modelinfo.go`** — the static context-window table SAM ships, which reveals the model families SAM's authors already track and the context sizes assumed.
7. **SAM docs** — `docs/documentation/installing/configure.md` (LLM provider section) and `airgap.md`, which state the `openai/` + `api_base` protocol-vs-backend rule and OpenAI-compatible-gateway support.

## Requirement → evidence map

| Requirement | Evidence |
|---|---|
| **H1 Native tool calling** | `client.go`: `ChatRequest.Tools []ToolDefinition`, `ChatResponse.ToolCalls []ToolCall`, `FinishReason` value `"tool_calls"`. `agent.go` branches on this to execute tools. No code path parses tool intent out of free text. |
| **H2 Streaming tool-call deltas** | `client.go`: `ChatCompletionStream` + `StreamChunk.ToolCallDeltas []ToolCallDelta{Index,ID,Name,ArgumentsDelta}`. `agent.go` reassembles per-index deltas into complete calls. Agents default to `supports_streaming: true`. |
| **H3 Multi-turn tool results** | `client.go`: `ChatMessage.Role` includes `"tool"`; `ToolCallID`, `ToolName` fields. `agent.go` appends tool results as `tool` messages and re-invokes the model. |
| **S1 tool_choice** | `bifrost.go:497` sets `params.ToolChoice` from `req.ToolChoice`. `structured/` uses forced/named tool choice. |
| **S2 Context window** | `modelinfo.go` maintains per-model `max_input_tokens`; used by the gateway's context-usage resolution. Multi-hop orchestration forwards tool results into subsequent turns, consuming context. |
| **S3 JSON arg fidelity** | `ToolCall.Arguments string` is JSON that SAM unmarshals for dispatch. Malformed JSON = dispatch failure. |
| **N1 Parallel tool calls** | `agent.go` handles `len(ToolCalls) > 1` and preserves parallel result order; `model.go` honors `parallel_tool_calls` config key. |
| **N2 Reasoning tokens** | `client.go`: `ReasoningConfig.BudgetTokens`, `StreamChunk.ReasoningDelta`, `Usage.ReasoningTokens`. `model.go` treats `thinking` as a non-completion key. |
| **N3 Prompt caching** | `client.go`: `CacheControl{Type,TTL}`; `model.go` `cache_strategy` non-completion key. |
| **N4 Vision** | `client.go`: `ContentBlock{Type:"image_url", ImageURL}`. |
| **Provider/protocol rule** | `configure.md`: "The prefix tells Bifrost which API protocol to use, not which backend model is running." `model.go` `knownProviders` includes `openai`, `ollama`, and 17 others. |

## Why the hard gates are exactly these three

The agent loop is, stripped down:

```
loop:
  resp = llm.ChatCompletionStream(req)         # needs streaming (H2)
  if resp.FinishReason == "tool_calls":        # needs native tool calls (H1)
      results = execute(resp.ToolCalls)
      req.Messages += assistant(resp.ToolCalls)
      req.Messages += tool(results)            # needs tool-result turns (H3)
      continue
  else:
      return resp.Content                       # final answer
```

Remove any one of H1/H2/H3 and this loop cannot complete a single tool-using task. Everything else changes *how well* or *how cheaply* the loop runs, not *whether* it runs. That's the principled basis for the hard/strong/nice split.

## Why compatibility is model-gated, not SAM-gated

SAM's provider layer (Bifrost/LiteLLM) already speaks to 19 named providers and any OpenAI-compatible endpoint. So SAM will happily *send* a tool-calling request to any of the 20 shortlisted models. Whether the model *answers correctly* — emits well-formed streaming tool calls and uses tool results — is a property of the model + its serving stack. Hence the shortlist ranks models by that property, and the harness validates it per-stack.

## Limits of this analysis

- Tool-calling **grades** in the shortlist are from community and vendor reports as of mid-2026, not from running all 20 through the harness in one lab. They're a prior, not a measurement. The harness turns the prior into a measurement for *your* stack.
- Context windows are commonly-served defaults; several models support more with RoPE scaling at some quality cost.
- Licenses change and vary by variant — always check the specific checkpoint's card.
- The SAM codebase evolves. The evidence citations are accurate as of the commit present when this repo was authored (`internal/llm/client.go` interface shape). Re-check against the current `client.go` if in doubt.
