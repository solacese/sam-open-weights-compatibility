# Capacity planning and total cost

The old “4-bit weights plus 15%” rule cannot size an enterprise service. Weight fit, single-request viability and useful throughput are different measurements. All numbers below are arithmetic examples, not hardware certifications or market prices.

## Account for the whole memory budget

```text
usable accelerator memory
  >= resident weights + quantization scales/metadata
   + KV cache / recurrent state + encoder and multimodal state
   + activations and workspaces + communication buffers
   + graph capture / allocator overhead + operational reserve
```

For an ordinary dense or MoE weight matrix, `parameters × bits / 8` gives a **weight-only lower bound** in bytes. A 27B model is about 54 GB at BF16 or 13.5 GB at ideal 4-bit storage, before scales, unquantized layers and runtime memory. Decimal GB and binary GiB are not interchangeable (`GiB = bytes / 2^30`). Use the actual checkpoint files and engine profiling.

For conventional full-attention GQA, a starting estimate is:

```text
KV bytes ≈ 2 × layers × KV_heads × head_dimension
           × cached_tokens_across_all_live_sequences × bytes_per_KV_element
```

Example: 32 layers, 8 KV heads, head dimension 128 and BF16 KV use about 128 KiB per token. At 32,768 cached tokens that is **4 GiB per sequence**; 16 such sequences need about **64 GiB** just for KV. Output tokens extend the cache too. Replicated KV, tensor parallel layout, fragmentation and block allocation change the actual result.

Do not apply that formula unchanged to sliding-window/hybrid attention, MLA, Mamba, DeltaNet, CED or compressed-cache architectures. DeepSeek V4.1 Flash also has Engram storage; Qwen Flash Next has additional n-gram embeddings and MTP. Profile the complete artifact, including host memory and offload bandwidth. [Publisher details are linked in each card](shortlist.md).

## Choose a topology by measured bottleneck

| Strategy | When to consider it | Cost / risk to measure |
|---|---|---|
| Independent replicas | Model fits; need concurrency and fault isolation | Extra full weight copies; load balance by queued tokens and cache locality |
| Tensor parallel | One replica needs more memory or bandwidth | Collective latency, interconnect topology, duplicated state; losing a rank loses the replica |
| Expert parallel for MoE | Supported kernels and sufficient expert traffic | All-to-all bandwidth, imbalance, topology, expert placement and failure domains |
| Pipeline parallel | Very large weights or supported cross-node recipe | Pipeline bubbles, scheduling complexity and tail latency |
| Prefill/decode separation | Long prompts dominate and combined serving wastes capacity | KV transfer, router complexity and two capacity pools; adopt only after a measured win |
| CPU / host offload | Architecture supports it and workload tolerates transfers | Host RAM, NUMA, pinned-memory use, storage and network bandwidth; not equivalent to GPU-resident latency |
| Smaller model / quantization | Baseline meets quality at lower cost | Schema/tool regressions and precision-specific kernel support |

NVIDIA H100/H200/B200/B300 and AMD Instinct deployments need separate validated runtime profiles. A quantized format's file size does not establish kernel support on every accelerator generation. Do not buy hardware from a model parameter count alone.

## Size requests and fleet separately

Record p50/p95/p99 input length, output and reasoning length, tool count, simultaneous tasks, burst arrival rate, modality mix, cancellation rate and latency target. Test cold and warm caches. Include queue time in latency.

As a first approximation, Little's law gives `in-flight requests ≈ arrival rate × service time`. If an agent task averages five sequential model calls and traffic reaches two tasks per second, the model service sees roughly ten calls per second before retries. With an average five-second service time, expect roughly 50 in-flight calls. Tool waits and fan-out alter this distribution; replay actual traces.

Calculate replica capacity from **sustainable task throughput within the SLO**, not peak tokens/second. Reserve capacity for maintenance and your declared failure domain. If one node carries an entire multi-GPU replica, “two pods” on that node do not provide node resilience. Validate spare placement and available GPU capacity before relying on autoscaling.

## Measure before tuning

1. Capture a baseline with fixed model/runtime/template and no optional optimizations.
2. Sweep context limits, output/reasoning budgets and concurrency against representative workloads.
3. Evaluate continuous batching, chunked prefill, prefix caching, KV precision and quantization one change at a time.
4. Add speculative decoding or disaggregation only after correctness and end-to-end latency measurements justify them. Draft overhead and acceptance rate can erase the gain.
5. Repeat the workload's tool/JSON evaluation after each optimization, then test overload and one failure domain unavailable.

[vLLM performance guidance](https://docs.vllm.ai/en/latest/configuration/optimization/) and the model-specific recipe are inputs, not universal optimal flags.

## TCO per successful business task

```text
monthly total = accelerator/host allocation + storage + network + energy/facility
              + software/support + platform/on-call labor + evaluation/security
              + reserved failover capacity
cost per successful task = monthly total / accepted completed tasks
```

Illustrative example: a fully loaded service costs 30,000 currency units per month and completes 2,000,000 attempted tasks with a 90% acceptance rate. Cost is `30,000 / 1,800,000 ≈ 0.0167` per accepted task. Include retries and failed attempts in resource cost; do not count them as successes. Compare API alternatives only under matching data, availability, latency and quality requirements, and obtain current quotes.

Include low utilization, peak reservations, model reload time, support coverage and engineering time. Routing everything to a large model or maintaining many idle specialist pools can both be expensive. Allocate usage and budgets per tenant and workload.
