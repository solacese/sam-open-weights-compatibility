# Methodology and evidence levels

Research cutoff: **15 October 2026**. This revision checks publisher model cards, downloadable metadata, checkpoint configuration and license text, plus current SAM source. It does not download full weights, run GPUs or certify compatibility.

## SAM source inspected

| Runtime | Immutable source | What was checked |
|---|---|---|
| Go | [SolaceDev/solace-agent-mesh-go @ 038d17c](https://github.com/SolaceDev/solace-agent-mesh-go/tree/038d17cd61c4ba19580c704774131ae8dc3a84f6) | Bifrost protocol selection and model config, typed tool calls, stream deltas and tool results |
| Python | [SolaceLabs/solace-agent-mesh @ f71e744](https://github.com/SolaceLabs/solace-agent-mesh/tree/f71e744842a66331a7dbb33e5fba8319dc892d12) | LiteLLM wrapper, ADK path, A2A streaming config and CLI layout |

Go paths, relative to the pinned tree:

- [`internal/llm/client.go`](https://github.com/SolaceDev/solace-agent-mesh-go/blob/038d17cd61c4ba19580c704774131ae8dc3a84f6/internal/llm/client.go): `ChatRequest.Tools`, `ToolChoice`, `ChatMessage.ToolCallID`, `StreamChunk.ToolCallDeltas`.
- [`internal/samapp/model.go`](https://github.com/SolaceDev/solace-agent-mesh-go/blob/038d17cd61c4ba19580c704774131ae8dc3a84f6/internal/samapp/model.go): `knownProviders`, `ParseModelConfig`, endpoint and request keys.
- [`internal/agentcore/agent.go`](https://github.com/SolaceDev/solace-agent-mesh-go/blob/038d17cd61c4ba19580c704774131ae8dc3a84f6/internal/agentcore/agent.go): assembling model responses and attaching tool results to conversation messages.
- [`docs/docs/documentation/installing/configure.md`](https://github.com/SolaceDev/solace-agent-mesh-go/blob/038d17cd61c4ba19580c704774131ae8dc3a84f6/docs/docs/documentation/installing/configure.md): provider prefix selects protocol.

Python paths:

- [`src/solace_agent_mesh/agent/adk/models/lite_llm.py`](https://github.com/SolaceLabs/solace-agent-mesh/blob/f71e744842a66331a7dbb33e5fba8319dc892d12/src/solace_agent_mesh/agent/adk/models/lite_llm.py): LiteLLM request and response conversion.
- [`src/solace_agent_mesh/agent/sac/app.py`](https://github.com/SolaceLabs/solace-agent-mesh/blob/f71e744842a66331a7dbb33e5fba8319dc892d12/src/solace_agent_mesh/agent/sac/app.py): `supports_streaming` configuration, documented as A2A streaming.

## Levels must not be collapsed

| Level | Meaning | Current repository status |
|---|---|---|
| Publisher-documented | Model artifact and capabilities described upstream | Catalog entries reach this level |
| Endpoint-probed | This exact endpoint passes the smoke checks | No live result recorded |
| SAM-validated | Real runtime trace shows dependent tool execution | No live result recorded |
| Workload-qualified | Held-out business tests pass agreed criteria | No result recorded |
| Production-approved | Security, licensing, capacity and failure gates accepted | No approval claimed |

The generator never turns a parser hint into a compatibility grade. `source_checked_at` is a research date, not a test date. `model_revision` identifies the inspected upstream snapshot, not an endorsed production release.

## Research rules

Use official publisher repositories and documentation. Store exact checkpoint IDs and immutable revisions; distinguish hosted aliases, announcements, base models and draft modules. Context comes from the inspected config/architecture parameters; documented extensions stay in notes. Preserve missing values instead of estimating a score or parser. Link license text separately from model metadata.

Recommendations are engineering judgments about which candidates to evaluate, with assumptions stated. Publisher benchmark tables are not independently reproduced. Compare only matched benchmark versions, harnesses and budgets. [Evaluation method](benchmarks.md).

The previous runner did not evaluate its printed assertions. It also assumed a universal SAM CLI shape. The replacement checks exported, normalized traces and returns an explicit incomplete result when none is supplied. Live trace extraction remains runtime-specific and must preserve provenance.
