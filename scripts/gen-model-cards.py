#!/usr/bin/env python3
"""Generate source-linked candidate cards and shortlist from models/index.csv."""
import argparse
import csv
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent


def slug(model_id):
    return re.sub(r"[^a-z0-9]+", "-", model_id.lower()).strip("-")


def outputs():
    with (ROOT / "models/index.csv").open() as source:
        rows = list(csv.DictReader(source))
    files = {}
    lines = ["# October 2026 model candidates\n",
             "Snapshot: **15 October 2026**. Listing order groups evaluation candidates; it is not a benchmark ranking. "
             "Every entry is **publisher-documented / SAM not run**. No live GPU or SAM validation results are claimed.\n",
             "Context below is the reference config/card limit, not a tested service capacity. "
             "Publisher extensions and special memory components are noted on each card. "
             "See [selection](pick-a-model.md), [capacity](capacity-planning.md), and [license review](licensing.md).\n",
             "| Candidate | Total / active parameters | Reference context | License | Suggested evaluation role |",
             "|---|---|---|---|---|"]
    for row in rows:
        name = slug(row["model_id"]) + ".md"
        lines.append(f"| [{row['model']}](../models/cards/{name}) | {row['total_parameters']} / {row['active_parameters']} | "
                     f"{int(row['config_context_tokens']):,} | {row['license']} | {row['candidate_role']} |")
        files[ROOT / "models/cards" / name] = f"""# {row['model']}

**Checked {row['source_checked_at']} · {row['evidence_status']} · SAM validation: {row['sam_validation']}**

| Field | Value |
|---|---|
| Checkpoint | `{row['model_id']}` |
| Publisher | {row['organization']} |
| Availability | {row['release_state']} |
| Revision | `{row['model_revision']}` |
| Total / active parameters | {row['total_parameters']} / {row['active_parameters']} |
| Reference context limit | {int(row['config_context_tokens']):,} tokens ({row['context_basis']}) |
| Weight license | [{row['license']}]({row['license_url']}) |
| Candidate role | {row['candidate_role']} |
| vLLM tool parser hint | `{row['vllm_tool_parser']}` |

{row['notes']}

[Publisher card at checked revision]({row['source_url']}) · [Serving recipe entry point]({row['serving_recipe_url']})

A parser hint is not a complete launch command. `see-recipe` means this catalog does not assert a parser name.
Select the runtime image, tokenizer, reasoning parser, chat template, quantization and hardware together.
Use the publisher's recipe, then pin and qualify that combination. [Serving guide](../../docs/serving.md).

## SAM model fragment

```yaml
model:
  model: openai/{row['model_id']}
  api_base: ${{LLM_API_BASE}}
  api_key: ${{LLM_API_KEY}}
  max_tokens: 4096
```

This fragment assumes the endpoint exposes the checkpoint ID. Replace it with your approved gateway alias when applicable.
The outer `openai/` selects a protocol; the remainder is the endpoint model ID. Configure output/reasoning budgets for your workload;
4096 is only a smoke-test budget. Parallel calls, forced tools and streaming need explicit validation for your SAM runtime.

## Qualify

```bash
export SAM_TEST_MODEL='openai/{row['model_id']}'
export SAM_TEST_API_BASE='http://127.0.0.1:8000/v1'
./scripts/probe.sh --report probe-result.json
```

Credentials come from `SAM_TEST_API_KEY`. A probe pass is endpoint evidence only.
Run real SAM traces, workload evaluation and operational gates before promotion: [validation](../../docs/validation.md).
"""
    lines.extend(["", "## Announcements and exclusions", "",
                  "- **Mistral Large 4:** API preview announced 6 October; publisher schedules weights for month end. "
                  "Excluded from downloadable candidates as of this snapshot. [Announcement](https://mistral.ai/news/mistral-large-4/).",
                  "- **Reflection Beam:** announced 501B / 23B active. Track checkpoint, license and supported serving evidence before qualification. "
                  "[Publisher announcement](https://reflection.ai/blog/introducing-beam). No SAM verdict recorded here.",
                  "- Hosted aliases and benchmarks do not establish that matching downloadable weights have the same features.",
                  "- Draft models, base checkpoints, guard classifiers, embeddings and rerankers are not interchangeable with agent models.",
                  "", "## Historical coverage", "",
                  "The original 25 rows remain in [legacy-2025.csv](../models/legacy-2025.csv) for migration reference. "
                  "Their grades, parser hints, hardware estimates and BFCL figures are historical, unverified claims, not current recommendations. "
                  "Existing qualified Llama 3, Qwen 2.5 or other deployments can remain useful; requalify before changing them.", ""])
    files[ROOT / "docs/shortlist.md"] = "\n".join(lines)
    return files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated content is stale")
    args = parser.parse_args()
    files = outputs()
    existing = set((ROOT / "models/cards").glob("*.md"))
    stale = existing - files.keys()
    changed = [p for p, content in files.items() if not p.exists() or p.read_text() != content]
    if args.check:
        if stale or changed:
            raise SystemExit(f"Generated content stale: {len(changed)} changed, {len(stale)} obsolete")
    else:
        for path in stale:
            path.unlink()
        for path, content in files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    print(f"{'Checked' if args.check else 'Generated'} {len(files) - 1} cards and shortlist")


if __name__ == "__main__":
    main()
