# Requirements Whitelist

Every requirement below is traced to a concrete place in the SAM codebase (`solace-agent-mesh-go`). This is what SAM *actually does*, not what a model vendor claims.

The three **HARD** gates are pass/fail: a model that fails any one of them cannot drive a SAM agent. **STRONG** requirements will work without them but degrade materially. **NICE** requirements are pure upside.

---

## HARD gates (must pass)

### H1 - Native tool / function calling (OpenAI `tools` schema)

SAM's agent loop is tool-call driven end to end. The LLM client models tools as first-class:

```go
// internal/llm/client.go
type ChatRequest struct {
    Tools      []ToolDefinition   // JSON-Schema tools sent to the model
    ToolChoice string             // "auto" | "none" | "required" | "<tool name>"
    ...
}
type ChatResponse struct {
    ToolCalls    []ToolCall        // model's requested calls
    FinishReason string            // "tool_calls" when the model wants a tool
}
```

The agent inspects `FinishReason == "tool_calls"`, executes the calls, feeds results back, and loops. A model that can only produce free text - even if you prompt it into a ReAct/JSON convention - is **not** compatible: SAM does not parse pseudo-tool-calls out of the content stream.

**Pass criterion:** the model, served OpenAI-style, returns `choices[].message.tool_calls[]` with a valid `function.name` and JSON `function.arguments` when given a `tools` array.

### H2 - Streaming with incremental tool-call deltas

SAM streams by default (`supports_streaming: true` is standard on agents) and assembles tool calls from partial chunks:

```go
// internal/llm/client.go
type ToolCallDelta struct {
    Index          int
    ID             string  // set on first delta for this call
    Name           string  // set on first delta for this call
    ArgumentsDelta string  // JSON fragment, concatenated across chunks
}
```

The 4-stage streaming pipeline in `internal/agentcore` reassembles `Name` + concatenated `ArgumentsDelta` per `Index`. Servers that return tool calls **only** in non-streaming mode, or that emit malformed/partial deltas, break the loop.

**Pass criterion:** with `"stream": true`, the endpoint emits `delta.tool_calls[]` chunks whose `index`, `id`, `function.name`, and incremental `function.arguments` reassemble into valid JSON.

### H3 - Multi-turn tool conversations (assistant tool_calls + `tool` role results)

After executing a tool, SAM appends the result as a `tool` role message keyed by call id, then asks the model to continue:

```go
// internal/llm/client.go
type ChatMessage struct {
    Role       string      // "system" | "user" | "assistant" | "tool"
    ToolCalls  []ToolCall  // on the assistant turn that requested tools
    ToolCallID string      // on the tool turn that answers a specific call
    ToolName   string
}
```

The model must accept its own prior `assistant` turn *with* `tool_calls`, plus one or more `tool` messages, and produce either a final answer or the next tool call. Models whose chat template can't represent a tool-result turn (or that hallucinate instead of using the returned data) fail here even if H1/H2 pass in isolation.

**Pass criterion:** given `[system, user, assistant(tool_calls), tool(result)]`, the model produces a coherent continuation that *uses* the tool result.

> **H1 + H2 + H3 together are the real filter.** Many open models pass H1 in a one-shot non-streaming test and still fail H2 or H3 in the actual agent loop. The [validation harness](validation.md) exercises all three.

---

## STRONG requirements (work without, but degrade)

### S1 - `tool_choice` control

```go
// internal/llm/bifrost.go
if req.ToolChoice != "" {
    params.ToolChoice = &schemas.ChatToolChoice{ ChatToolChoiceStr: ... }
}
```

SAM sets `tool_choice` (commonly `auto`; `required`/named for forced-tool and structured-output paths in `internal/agentcore/structured`). Models that ignore `tool_choice: required` can skip a mandatory tool call, which breaks flows like the JDE `format_disclaimer` mandatory-call pattern.

### S2 - Context window ≥ 32K (128K+ recommended)

`internal/llm/modelinfo/modelinfo.go` tracks per-model context windows because orchestration forwards tool results, carries system prompts + history, and fans out to multiple agents. Multi-hop scenarios overflow small windows. 32K is the practical floor for a single leaf agent; **128K+** for an orchestrator.

### S3 - Faithful JSON arguments

Tool arguments arrive as a JSON string SAM must `json.Unmarshal`. Models that emit trailing prose, markdown fences, or malformed JSON in `function.arguments` cause tool dispatch failures. Quality here varies more by *quant level and serving template* than by model family - validate it.

---

## NICE to have (upside)

### N1 - Parallel tool calls

```go
// internal/agentcore/agent.go - handles len(ToolCalls) > 1 and preserves
// the relative order of parallel tool results.
```

SAM supports and orders multiple tool calls in one turn. The config key `parallel_tool_calls` (from `internal/samapp/model.go`) is passed through to the model. Absence just serializes fan-out - slower, still correct.

### N2 - Reasoning / thinking tokens

```go
// internal/llm/client.go
type ReasoningConfig struct { BudgetTokens int }   // ChatRequest.Reasoning
// StreamChunk.ReasoningDelta carries streamed thinking text
```

Configured via the `thinking:` model key (a `nonCompletionKey` in `internal/samapp/model.go`). Improves deliberate tool selection for models that support it (DeepSeek-R1, some Qwen). Optional.

### N3 - Prompt caching

```go
// internal/llm/client.go
type CacheControl struct { Type string; TTL string }   // "ephemeral", "" | "1h"
```

Driven by the `cache_strategy` model key. Pure cost/latency optimization; most open-weights servers don't implement it - no functional impact.

### N4 - Vision (image input)

```go
// internal/llm/client.go
type ContentBlock struct { Type string /* "image_url" */; ImageURL string }
```

Only needed for agents that process images/artifacts. Restricts you to VL model variants (Qwen2.5-VL, Llama 3.2 Vision, etc.).

---

## Config keys SAM honors (for your model YAML)

These are parsed by `internal/samapp/model.go` (`knownModelConfigKeys` + `nonCompletionKeys`) and map 1:1 to Python SAM's `lite_llm.py`:

| Key | Purpose |
|---|---|
| `model` | `provider/model` string (use `openai/<name>` for OpenAI-compatible endpoints) |
| `api_base` | Endpoint URL (your vLLM/Ollama/etc. `/v1`) |
| `api_key` / `api_key_file` | Auth (many local servers ignore it - send any value) |
| `temperature`, `max_tokens` | Sampling |
| `parallel_tool_calls` | Toggle parallel tool calling (N1) |
| `thinking` | Reasoning budget (N2), e.g. `{type: enabled, budget_tokens: 2048}` |
| `cache_strategy` | Prompt caching (N3) |
| `num_retries`, `request_timeout_seconds` | Transient-error handling |
| `extra_headers` | Custom headers (e.g. corporate proxy) |
| `oauth_*` | OAuth2-secured gateway auth |
| `api_skip_tls_verify`, `api_ca_cert` | TLS for self-signed endpoints |

> **Provider prefix rule (from the docs):** the prefix tells Bifrost which *API protocol* to speak, **not** which backend model runs. A LiteLLM/vLLM proxy fronting *any* open model uses the `openai/` prefix + `api_base`. `ollama/` is a first-class prefix for Ollama. Full provider list in `internal/samapp/model.go` `knownProviders`.

## The decision, in one flowchart

```
Is the model served behind an OpenAI-compatible API?  ──no──▶  put a server in front (vLLM/Ollama/TGI/LiteLLM)
        │yes
Does it emit OpenAI tool_calls?  ──no──▶  NOT COMPATIBLE
        │yes
Does it emit them while streaming (H2)?  ──no──▶  NOT COMPATIBLE
        │yes
Does it use a tool-result turn correctly (H3)?  ──no──▶  NOT COMPATIBLE
        │yes
Context ≥ 32K? honors tool_choice?  ──no──▶  usable but LIMITED (leaf agents / no forced tools)
        │yes
✅ SAM-compatible. Run the harness to confirm on your stack.
```
