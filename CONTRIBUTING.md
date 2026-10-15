# Contributing

Keep candidate discovery separate from compatibility evidence. A new model row must include its exact publisher ID, immutable revision, checked date, weight license link, context source, known serving entry point and limitations. Use `see-recipe` for an unverified parser, not an invented name. Do not copy hosted features into a downloadable checkpoint or carry a benchmark score between revisions.

Update `models/index.csv`, then run:

```bash
python3 scripts/gen-model-cards.py
python3 scripts/check-catalog.py
python3 -m unittest discover -s tests -p 'test_*.py'
bash -n scripts/probe.sh scripts/run-sam-scenario.sh
```

Cards and the shortlist are generated; edit the CSV or generator instead of their outputs. The offline catalog checker intentionally preserves the current `not-run` boundary. A contribution adding real validation must include a reviewed evidence format and adjust that policy explicitly.

For any claimed result, identify the deployment bundle and attach sanitized, reproducible evidence with sample counts and acceptance criteria. Never commit credentials, confidential prompts, raw customer traces or private endpoint names. Synthetic harness tests prove the checker, not a model.

For external evidence, use primary sources and date them. Do not sort mixed benchmark versions, imply a support certification, or describe a preview as downloadable. Keep historical rows in `models/legacy-2025.csv` as a historical artifact.
