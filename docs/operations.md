# Operations, release and rollback

An approved model service is a versioned product. Publish a stable internal alias and make every alias change traceable to a qualified artifact bundle.

## Versioned deployment bundle

Record: SAM runtime/commit and adapter, model revision and hashes, tokenizer/template hashes, parser versions, runtime image digest, driver/framework/kernel versions, GPU topology, quantization and KV/state precision, request limits, reasoning/sampling defaults, gateway policy and evaluation dataset version.

Use `tests/results/qualification-template.json` as a starting record. Blank values mean incomplete evidence. The model catalog's inspected revision is not a substitute for a locally approved bundle.

## Service-level measurements

| Signal | What to track | Action |
|---|---|---|
| Task success | Accepted business outcomes and schema/tool errors by workload | Regressions block promotion even if token throughput improves |
| Latency | Queue, time to first token, inter-token, full call and full agent task; p50/p95/p99 | Budget queue and reasoning time separately |
| Saturation | Queued tokens, live sequences, cache/state occupancy, GPU memory and utilization | Enforce admission limits before OOM or unbounded waiting |
| Reliability | 429/5xx, timeouts, broken streams, restarts and cold-load time | Diagnose gateway/server/tool boundaries separately |
| Cost | Input/output/reasoning usage, retries and accepted tasks per tenant | Apply budgets and alert on runaway loops |
| Security | Denied identity/tool/egress events and policy violations | Preserve minimal audit context and route to the owner |

Use bounded labels such as alias, tenant class, workload and status. Do not put prompts, user IDs, tool payloads or unconstrained task IDs into metric labels. Restrict detailed traces and use short retention where content is needed. [vLLM metrics](https://docs.vllm.ai/en/latest/usage/metrics/).

## Overload and recovery behavior

- Bound queue length, request body, input/output/reasoning tokens, media size, tool fan-out and task/model-call count. Return predictable errors rather than silently truncating or switching models.
- Use deadlines across gateway, server, SAM and tools. Verify that disconnect/cancellation stops generation and releases capacity.
- Retry transient failures with bounded backoff and jitter within the task deadline. Do not automatically replay partially delivered streams or non-idempotent tool writes.
- Use startup/readiness checks that tolerate weight load and kernel warmup. Keep liveness conservative enough to avoid restart loops during long initialization.
- Drain replicas before termination. Reserve reload/canary capacity and measure model artifact transfer time. Autoscaling cannot create scarce GPUs instantly.
- Test one node/replica failure, distributed-rank loss, tool timeout, identity outage, storage unavailable and loss of external network. Document degraded operation and restore time.
- Keep session/task state and business-side effects durable where required. An available inference replica does not restore a lost workflow.

## Release gates

| Stage | Required evidence before advancing |
|---|---|
| Acquire | Provenance, hashes, licenses, vulnerabilities and offline startup |
| Protocol | Endpoint probe plus tool-choice, parallel and interruption cases used by the application |
| SAM | Real, non-mocked runtime traces through the deployed gateway |
| Workload | Held-out task acceptance, safety/authorization behavior, language and long-context tests |
| Load / failure | Agreed latency/concurrency envelope, overload response and failover drill |
| Canary | Limited approved traffic, version tags, business metrics and named rollback owner |
| General availability | Signed approval, on-call, capacity and rollback artifacts ready |

Use shadow traffic only where policy allows duplicating the data. Disable side-effect tools in shadow runs. Canary by a small tenant/workload cohort with a verified rollback route. Never allow a gateway to silently fall back to an external model when the data policy requires self-hosting.

## A bounded adoption plan

An example sequence, not a promised schedule:

1. Define one business workflow, data classification, licenses, baseline and acceptance thresholds.
2. Qualify two candidate bundles and a private endpoint; run protocol and real SAM tests.
3. Replay held-out workloads and load profiles; harden identities, tool boundaries and egress.
4. Run the declared failure drills and offline restart, then admit a limited cohort.
5. Review task success, p95/p99 task latency and cost per accepted task before expanding.

The application owner decides task readiness; platform ownership alone cannot approve business action correctness.
