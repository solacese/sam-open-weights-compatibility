# Evaluation and benchmark evidence

The previous table sorted mixed BFCL versions and sometimes reused a score from a different checkpoint. It also treated parser availability as a compatibility verdict. Those numbers remain only in [historical data](../models/legacy-2025.csv); this edition publishes **no new numeric leaderboard ranking** without a reproducible matching snapshot.

## Use external benchmarks for candidate discovery

[Berkeley Function-Calling Leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html) is useful for tool selection, argument correctness and multi-turn behavior. A Prompt-mode result is not evidence of native API `tool_calls`. Compare the exact checkpoint, benchmark version, native/prompt mode, harness, reasoning budget, sample count and date.

Coding, terminal, research and office-work benchmarks can reveal promising candidates. Publisher scores are claims under their own harness and budgets, not measurements of SAM. Hosted aliases may differ from downloadable weights. A model's absence from a leaderboard is missing evidence, not a score of zero or proof that it was never tested elsewhere.

The [vLLM parser documentation](https://docs.vllm.ai/en/latest/features/tool_calling/) and publisher recipes establish available serving paths. They do not measure argument fidelity or successful agent execution on your runtime.

## Enterprise evaluation pack

| Dimension | Representative tests | Record |
|---|---|---|
| Tool selection | Relevant, irrelevant, ambiguous and missing-information requests; many similar tools | Correct call/no-call rate; inappropriate action attempts |
| Argument correctness | Nested objects, enums, Unicode, escaping, optional/null fields and boundary values | Schema-valid AND semantically correct arguments |
| Multi-turn | Dependent calls, changing results, errors, retries and contradictory outputs | Correct use of observed values and termination within call budget |
| Reasoning | On/off/effort, adequate output budget, history preservation | Task success, tokens and end-to-end latency |
| Retrieval | Permission-scoped documents, citations, outdated and conflicting material | Grounding, abstention and ACL enforcement |
| Language / vision | Actual user languages, scans, tables, charts and large media | Quality plus preprocessing and memory costs |
| Security | Injection in documents/tool output, unauthorized IDs, prohibited actions | Authorization enforced by code and policy, with auditable results |
| Performance | Real prompt/result distributions, bursts, cold/warm cache and cancellations | Task p50/p95/p99, sustainable throughput and accepted-task cost |
| Resilience | Replica loss, tool/identity/storage outage, broken streams | Error containment, no duplicate writes, recovery time |

## Make results comparable

Freeze the dataset, expected business outcomes and evaluation code. Split development and held-out cases; keep confidential data in the approved environment. Run the same request/tool harness and budgets for each candidate. Include negative cases and repeated runs because sampling makes results variable.

Report numerator and denominator, not just a percentage. Separate protocol failures, tool failures, model mistakes, timeouts and policy denials. Include confidence intervals for important acceptance rates and disclose judge model/prompt versions if using model grading. Manually audit a sample, particularly business actions and security cases.

A useful result reads: “bundle X completed 187/200 held-out tasks under a 32K service context, defined tool permissions and a 60-second task deadline; 5 schema errors, 6 incorrect outcomes and 2 timeouts.” It does not read “excellent, production-proven.” This example is illustrative, not a recorded measurement.
