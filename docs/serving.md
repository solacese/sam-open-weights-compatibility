# Serve an approved model for SAM

Use the publisher's recipe for the exact checkpoint, accelerator and weight format, then pin a working runtime image. A generic “OpenAI-compatible” label does not verify tool parsing, reasoning history, streaming or schema coverage.

## Engine selection

| Engine / platform | Sensible evaluation role | Qualification focus |
|---|---|---|
| vLLM | Shared production inference, supported dense/MoE checkpoints | Model support, tool + reasoning parsers, precision-specific kernels, memory and distributed topology |
| SGLang | Production candidate where its checkpoint recipe is established | Exact parser flags and template, scheduling, distributed behavior and observability |
| NVIDIA NIM / TensorRT-LLM / Dynamo | Organizations standardizing supported NVIDIA inference profiles | Supported hardware/model profile, build artifacts, software terms and operational ownership |
| KServe / Kubernetes model platform | Lifecycle, routing and deployment orchestration around an engine | Tenant policy, rollout, autoscaling and GPU scheduling; does not add model tool-calling capabilities |
| Ollama / llama.cpp | Local development, constrained edge or dedicated small services | Exact quant/template, protocol behavior and concurrency; separately design enterprise auth and operations |
| Hugging Face TGI | Existing qualified installations | Upstream is in maintenance mode; not the default new-platform recommendation |
| LiteLLM or another inference gateway | Optional policy/routing layer | Adapter fidelity, identity, quotas, timeouts, streaming pass-through and no prohibited fallback |

Sources: [vLLM](https://docs.vllm.ai/en/latest/), [SGLang](https://docs.sglang.ai/), [NVIDIA inference](https://docs.nvidia.com/nim/large-language-models/latest/), [Dynamo](https://docs.nvidia.com/dynamo/latest/), [KServe](https://kserve.github.io/website/), [TGI maintenance notice](https://huggingface.co/docs/text-generation-inference/en/index).

A gateway translates or governs requests; it does not turn an arbitrary text model into a reliable tool caller.

## Concrete local smoke-test recipe: Qwen3.6 35B A3B with vLLM

The [checked publisher card](https://huggingface.co/Qwen/Qwen3.6-35B-A3B/blob/995ad96eacd98c81ed38be0c5b274b04031597b0/README.md) documents `qwen3_coder` for tool calls and `qwen3` for reasoning. This reduced-context example is a **starting configuration, not a tested deployment**. Use a reviewed, pinned vLLM environment with this architecture supported; set tensor parallelism for your measured hardware capacity.

```bash
export MODEL_REVISION='995ad96eacd98c81ed38be0c5b274b04031597b0'
export TP_SIZE=2   # illustrative; qualify memory and throughput on your actual GPUs
vllm serve Qwen/Qwen3.6-35B-A3B \
  --revision "$MODEL_REVISION" \
  --served-model-name sam-candidate \
  --host 127.0.0.1 --port 8000 \
  --tensor-parallel-size "$TP_SIZE" \
  --max-model-len 32768 \
  --max-num-seqs 8 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder \
  --reasoning-parser qwen3
```

The vendor's full-context recipe uses a larger topology. Lowering context and request concurrency changes the evaluation envelope; it does not validate quality at 256K. No quantization is implied above. Do not combine a 4-bit memory estimate with an unquantized launch.

```bash
export SAM_TEST_MODEL='openai/sam-candidate'
export SAM_TEST_API_BASE='http://127.0.0.1:8000/v1'
./scripts/probe.sh --report probe-result.json
```

Bind a local experiment to loopback. For a deployed service, use a private gateway with TLS and authenticated workload access, and allow traffic only from the gateway to the model server. In a container the server may need a private-interface bind; do not publish it as an unauthenticated public endpoint. [Enterprise controls](enterprise-self-hosting.md).

## Model-specific traps

- Qwen3.8 variants have different architecture and license details. Follow their own recipe links; do not assume the Qwen3.6 launch applies unchanged.
- For gpt-oss, the server must correctly implement Harmony, including tool calls and reasoning. Do not replace its template with a generic chat template. [OpenAI implementation checks](https://developers.openai.com/cookbook/articles/gpt-oss/verifying-implementations).
- Mistral checkpoints may require their tokenizer/config flags in addition to `--tool-call-parser mistral`; reasoning models also need the documented reasoning parser.
- New DeepSeek, Kimi and Nemotron architectures can require special kernels, offload configuration, custom code or a specific engine build. Review those artifacts before admitting them into an enterprise registry.
- Publisher hub pages often generate a generic `vllm serve` snippet automatically. Prefer the authored model card's deployment section or linked engine cookbook, not that auto-generated snippet alone.
- Do not add `trust_remote_code`, a nightly image or a downloaded parser plugin to a production service without reviewing and pinning the added code.

See [each candidate card](shortlist.md) for the checked publisher recipe entry point. `see-recipe` is an explicit unknown parser hint; it is not a literal CLI argument.

## SAM model fragment and gateway alias

```yaml
model:
  model: openai/enterprise-orchestrator
  api_base: ${LLM_API_BASE}
  api_key: ${LLM_API_KEY}
  max_tokens: 4096
```

Embed this fragment in the configuration supported by your installed SAM version. Set secrets through your deployment's secret provider. Keep the `openai/` protocol prefix even when the underlying model is Qwen, Mistral or gpt-oss. The endpoint must expose `enterprise-orchestrator`; record the artifact bundle to which the gateway resolves it.

Do not copy model-independent temperature, thinking or parallel-tool defaults into every family. Start with the publisher's guidance, confirm which settings the adapter forwards, and qualify the actual request envelope. A 4096-token limit is only a smoke-test setting and can truncate a reasoning model before its first tool call.

## Verify the gateway as well as the server

Run the same probe directly against the private server in the test environment and through the deployed gateway. Compare call IDs, tool names/arguments, streaming termination, errors, usage, request limits and cancellation. A gateway can buffer SSE or strip reasoning/tool fields even when the backend is correct. The final acceptance test uses the exact route SAM will call.
