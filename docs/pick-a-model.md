# Pick a model for an enterprise SAM deployment

Snapshot: **15 October 2026**. The recommendations below are evaluation priorities based on publisher capabilities, licensing and operational complexity. They are not measured SAM rankings. Use the [catalog](shortlist.md) for checkpoint-specific sources.

## A practical starting portfolio

Start with two or three candidates and the actual business workflow. A fleet of specialist models creates routing, spare-capacity and upgrade costs of its own.

| Workload / constraint | Evaluate first | Reason and qualification focus |
|---|---|---|
| High-volume leaf tools, extraction, classification | Qwen3.5 9B; Ministral 3 14B; Gemma 4 12B | Smaller replicas; measure argument accuracy, abstention and multilingual coverage |
| General enterprise routing and document work | Qwen3.8 27B; Qwen3.6 35B A3B; Gemma 4 31B / 26B A4B | Moderate model footprint; test dependent tools and noisy document inputs |
| Larger orchestration with permissive weight terms | Mistral Small 4; gpt-oss 120b; GLM 5.3 Flash | Different memory, reasoning and template requirements; compare cost per successful task |
| Coding agents | Devstral Small 2; Kimi K2.7 Code; GLM 5.3 | Evaluate repository tasks in sandboxes; review custom license terms where applicable |
| Frontier model platform with dedicated GPU networking team | DeepSeek V4.1 Flash / V4 Pro 0813; Kimi K3; Qwen3.8 2.4T; Nemotron 3 Ultra | Specialized kernels, large weight stores, offload/interconnect and failure recovery matter |
| Existing NVIDIA platform investment | Nemotron 3.5 Lightning / Super VL; Nemotron 3 Super / Ultra | Qualify exact weight format, engine build, hybrid-state handling and license; compare against simpler replicas |
| Preference for Mistral with downloadable Apache weights | Small 4, Large 3, Ministral 3, Devstral Small 2 | Medium 3.5 has a company revenue restriction; Large 4 weights are still pending at this cutoff |

These are alternatives to evaluate, not a claim that all fit one GPU. [Capacity planning](capacity-planning.md) replaces the old universal “4-bit + 15%” sizing table.

## Selection sequence

1. Define the data boundary: internal-only, external customers, restricted documents, residency, offline requirement and permitted tool actions.
2. Review the **exact weight license** and any quantizer, tokenizer, runtime and support terms. “Open weights” is not a commercial permission category. [License review](licensing.md).
3. Set task acceptance criteria: correct business result, valid arguments, appropriate abstention, language coverage, latency and cost ceiling.
4. Establish a smaller baseline and a larger challenger. Reuse an already qualified model as a control rather than changing every component at once.
5. Pick a supported serving recipe for the checkpoint, hardware and precision. Preserve the vendor's sampling and reasoning guidance initially.
6. Run the endpoint probe, real SAM scenarios and held-out workloads, then load/failure/security tests. Record every version.
7. Promote only after the platform and application owners accept the measured envelope. Keep the previous bundle available for rollback.

## Tradeoffs that change the answer

- **Reasoning budget:** higher effort can improve tool selection but increases decode latency and memory residency. Lower per-turn latency can still produce slower tasks through extra retries.
- **MoE:** active parameters describe part of compute, not total resident or offloaded weight storage. New lookup memories and draft modules make the distinction even larger.
- **Long context:** an advertised million-token window says little about latency, concurrency or retrieval quality on your infrastructure. Evaluate RAG and compaction before increasing every request limit.
- **Multimodality:** image encoders and media processing add memory, request limits and URL-fetch security concerns. Text-only SAM flows do not prove a vision path.
- **Quantization:** compare tool arguments, multilingual quality and task completion at the intended precision. A smaller quantized model can be operationally cheaper even when a larger model wins a benchmark.
- **Publisher geography:** review organizational policy and supply-chain provenance, but distinguish the model's origin from the location of inference, telemetry, storage, support access and outbound tool calls.

## Do not replace a qualified model only because it is older

Llama 3, Qwen 2.5, gpt-oss and other established deployments can remain valid controls. A new release must earn promotion on your workload. The [historical CSV](../models/legacy-2025.csv) preserves earlier coverage without carrying its unverified grades into the current shortlist.
