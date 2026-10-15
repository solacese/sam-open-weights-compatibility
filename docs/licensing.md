# Weight licenses and enterprise procurement

Checked **15 October 2026**. This is a procurement screening guide; the exact pinned license and your organization/use determine the decision. Have the accountable reviewer resolve terms before promotion. Engine licenses, support subscriptions, model weights and training data are separate artifacts.

## Important checkpoint differences

| Checkpoint / family in this catalog | Terms observed | Enterprise review trigger |
|---|---|---|
| Qwen3.8 27B; Qwen3.6 35B A3B; Qwen3.5 9B | Apache-2.0 | Preserve notices and review the full distribution |
| Qwen3.8 Flash Next | Qwen Community 1.0 | Separate commercial license for defined Model as a Service / AI Work Assistant businesses; internal-use exception is narrowly defined |
| Qwen3.8 2.4T A95B | Custom Qwen3.8-Max terms | Different business/revenue condition from Flash Next; do not assume the same terms across Qwen3.8 |
| Gemma 4 checkpoints listed here | Apache-2.0 | Do not carry over older Gemma license assumptions |
| Mistral Small 4, Large 3, Ministral 3, Devstral Small 2 | Apache-2.0 | Verify exact variant and any redistributed runtime |
| Mistral Medium 3.5 | Modified MIT | License excludes companies/employers above USD 20M global consolidated monthly revenue for the preceding month; request commercial terms if applicable |
| DeepSeek V4.1 Flash / V4 Pro 0813 | MIT | Review auxiliary components and deployment artifacts too |
| GLM 5.3 Flash | MIT | Distinct from GLM 5.3 |
| GLM 5.3 | Custom GLM 5.3 terms | Security-review requirement for defined Model as a Service businesses above an aggregate revenue threshold |
| Kimi K2.7 Code | Modified MIT | Review attribution and large-scale commercial conditions |
| Kimi K3 | Custom Kimi K3 | Separate agreement for defined Model as a Service businesses above revenue threshold; attribution conditions and defined internal-use exception |
| Nemotron 3 Super BF16 | NVIDIA Nemotron Open Model License | Weight license differs from NIM software/product terms |
| Nemotron 3 Ultra NVFP4; Nemotron 3.5 Lightning / Super VL | OpenMDW 1.1 | Different from Super; preserve its governing license |
| gpt-oss 20b / 120b | Apache-2.0 | Preserve notices; separately review dependencies and use policies |

Sources: license links and pinned publisher declarations in [models/index.csv](../models/index.csv) and every generated card. Google publishes its Gemma 4 license on its documentation site; several Mistral Apache checkpoints declare their license in the pinned card without a separate LICENSE file. Retain the publisher declaration with the applicable license text. Particularly relevant texts: [Qwen Flash Next](https://huggingface.co/Qwen/Qwen3.8-Flash-Next/blob/de4b8e4d43b917e7706784d8bb445c9af86a3540/LICENSE), [Qwen 2.4T](https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B/blob/207bd685a7e3696cfaff12ded7c6a7ea0f88c996/LICENSE), [Mistral Medium 3.5](https://huggingface.co/mistralai/Mistral-Medium-3.5-128B/blob/main/LICENSE), [GLM 5.3](https://huggingface.co/zai-org/GLM-5.3/blob/main/LICENSE), [Kimi K3](https://huggingface.co/moonshotai/Kimi-K3/blob/main/LICENSE).

The summaries intentionally omit some definitions and obligations. An internal tool that serves affiliates, customers or partners may not satisfy a license's internal-use exception. Interpret the actual license rather than inferring permission from a model hub tag.

## Keep a promotion record

- Exact legal entity, intended internal/external use and approved user population.
- Weight/tokenizer/template revision, license text hash and required notices.
- Fine-tuning, derivative, redistribution and quantization provenance.
- Applicable custom-license conditions, approvals or commercial agreement reference.
- Runtime/container/support terms, vulnerability response and end-of-life commitments.
- Data-processing map: inference, retention, telemetry, support access and tool egress.
- Accountable owner, approval date and review trigger.

Recheck when the checkpoint, derivative, organization, business model or user population changes. A weight license does not establish privacy, residency, sector compliance or rights to enterprise input data.
