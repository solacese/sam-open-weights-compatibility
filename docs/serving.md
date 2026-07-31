# Serving Open Models for SAM

SAM needs an **OpenAI-compatible** endpoint. The recipes below stand one up for each common server, plus the SAM `model:` block that points at it. The golden rule from the SAM docs:

> The `openai/` prefix tells Bifrost which **API protocol** to speak — not which model runs. A proxy fronting *any* open model uses `openai/` + `api_base`. `ollama/` is a first-class prefix for Ollama.

The critical detail for SAM is **tool calling must work while streaming (H2)**. Most servers need an explicit tool-call parser flag for that. Each recipe calls it out.

---

## vLLM (recommended for production)

```bash
vllm serve Qwen/Qwen2.5-32B-Instruct \
  --host 0.0.0.0 --port 8000 \
  --enable-auto-tool-choice \
  --tool-call-parser hermes \
  --max-model-len 32768
```

- `--enable-auto-tool-choice` + `--tool-call-parser <parser>` are **required** for H1/H2. Pick the parser that matches the model family:
  | Model family | `--tool-call-parser` |
  |---|---|
  | Qwen2.5 / Qwen2.5-Coder | `hermes` |
  | Llama 3.1 / 3.3 | `llama3_json` |
  | Mistral / Mixtral / Mistral Small/NeMo | `mistral` |
  | Command R / R+ | `hermes` (or model-specific in recent vLLM) |
  | DeepSeek-V3 / R1 | `deepseek_v3` |
- Serving a quantized checkpoint? Add `--quantization awq` (or `gptq`, `fp8`) and use the matching quantized repo. **Aggressive quant degrades JSON-arg fidelity (S3) — validate.**

SAM `model:` block:

```yaml
model:
  model: openai/Qwen/Qwen2.5-32B-Instruct   # openai/ = protocol; name = whatever vLLM serves
  api_base: http://localhost:8000/v1
  api_key: sk-noop                          # vLLM ignores unless --api-key set
  parallel_tool_calls: true
  temperature: 0.2
  max_tokens: 4096
```

---

## SGLang (high-throughput alternative)

```bash
python -m sglang.launch_server \
  --model-path Qwen/Qwen2.5-32B-Instruct \
  --host 0.0.0.0 --port 8000 \
  --tool-call-parser qwen25
```

SGLang exposes an OpenAI-compatible `/v1`. Same SAM block as vLLM (point `api_base` at `:8000/v1`). Confirm the tool-call parser matches your model; SGLang's parser names differ from vLLM's.

---

## Ollama (fastest local dev)

```bash
ollama pull qwen2.5:32b
ollama serve            # serves OpenAI-compatible API on :11434/v1
```

Ollama is a **first-class SAM provider prefix**:

```yaml
model:
  model: ollama/qwen2.5:32b
  api_base: http://localhost:11434
```

Or via the OpenAI-compat path:

```yaml
model:
  model: openai/qwen2.5:32b
  api_base: http://localhost:11434/v1
  api_key: ollama
```

Ollama tool calling works for tool-capable models (Qwen2.5, Llama 3.1/3.3, Mistral) but **streaming tool-call support has historically lagged** — run `probe.sh` check 2 (H2) before relying on it. Great for dev, validate for prod.

---

## Text Generation Inference (TGI)

```bash
docker run --gpus all -p 8000:80 \
  ghcr.io/huggingface/text-generation-inference:latest \
  --model-id Qwen/Qwen2.5-32B-Instruct
```

TGI's `/v1/chat/completions` is OpenAI-compatible and supports tools/`tool_choice` on recent versions. SAM block:

```yaml
model:
  model: openai/Qwen/Qwen2.5-32B-Instruct
  api_base: http://localhost:8000/v1
  api_key: sk-noop
```

---

## LiteLLM proxy (front many backends as one)

Useful when you want SAM to see one endpoint but route to several open models, or to add auth/logging.

`litellm-config.yaml`:

```yaml
model_list:
  - model_name: qwen-32b
    litellm_params:
      model: openai/Qwen/Qwen2.5-32B-Instruct
      api_base: http://vllm-host:8000/v1
      api_key: sk-noop
  - model_name: llama-70b
    litellm_params:
      model: openai/meta-llama/Llama-3.3-70B-Instruct
      api_base: http://vllm-host2:8000/v1
      api_key: sk-noop
```

```bash
litellm --config litellm-config.yaml --port 4000
```

SAM block:

```yaml
model:
  model: openai/qwen-32b            # the LiteLLM model_name
  api_base: http://localhost:4000
  api_key: ${LITELLM_KEY}
```

This is exactly the pattern a corporate inference gateway (e.g. an internal MaaS) uses — SAM points at the gateway with `openai/` + `api_base` + a virtual key, and the gateway fans out to the real backends.

---

## Air-gapped / on-prem

SAM supports fully air-gapped deployment. Any in-cluster vLLM/SGLang/TGI/LiteLLM works via `openai/` + an internal `api_base`. For self-signed TLS on the endpoint:

```yaml
model:
  model: openai/Qwen/Qwen2.5-32B-Instruct
  api_base: https://llm.internal:8443/v1
  api_ca_cert: /etc/ssl/certs/internal-ca.pem   # or api_skip_tls_verify: true (dev only)
  api_key_file: /var/run/secrets/llm/api_key     # file-based secret (K8s/Docker)
```

See the SAM air-gap docs for the broader offline story.

---

## Serving checklist for SAM

- [ ] Endpoint answers `GET /v1/models` (OpenAI-compatible).
- [ ] Tool-call parser flag set and matches the model family.
- [ ] `probe.sh` H1 (tool call) PASS.
- [ ] `probe.sh` H2 (streaming tool call) PASS — **this is the one servers most often miss.**
- [ ] `probe.sh` H3 (tool-result turn) PASS.
- [ ] Context window (`--max-model-len` / server config) ≥ your agent's need (32K leaf, 128K orchestrator).
- [ ] Quant level validated for JSON-argument fidelity if using AWQ/GPTQ/FP8.
- [ ] SAM `run-sam-scenario.sh two-tool-dependency` PASS.
