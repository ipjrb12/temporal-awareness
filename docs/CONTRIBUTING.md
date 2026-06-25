# Contributing — an Open Safety Project

**New to AI safety? You're exactly who this guide is for.**

Temporal Awareness is an **Open Safety Project**: a research effort built so that people who
are new to AI safety can make real contributions with a low barrier to entry. You don't need
a PhD, a GPU, or prior interpretability experience to help. You need curiosity and a
willingness to learn in the open.

This guide gets you from "I just found this repo" to "I opened my first pull request."

---

## 1. What is this project, in one minute?

Large language models make decisions that play out over **time** — short-term vs long-term.
This project studies how a model **internally represents time horizons**, whether that internal
sense matches what the model *says*, and what happens to its behavior (including its safety
behavior) over long interactions.

Why it matters: as AI agents run for longer and more autonomously, we want to **read their
time-horizon "intentions" directly from their activations** — not just trust their words. A
key finding is that a model's safety behavior can **drift over long or repetitive sessions**,
and a simple probe can see it coming.

For the full picture: [`docs/RESEARCH_PROGRAM.md`](RESEARCH_PROGRAM.md) and
[`docs/RELATED_WORK.md`](RELATED_WORK.md).

---

## 2. Set up in 5 minutes

```bash
# Clone
git clone https://github.com/justinshenk/temporal-awareness
cd temporal-awareness

# Install (uv is recommended; plain pip works too)
uv pip install -e ".[dev]"      # or: pip install -e ".[dev]"

# Copy env template (only needed for experiments that call model APIs)
cp .env.example .env

# Sanity check — verify the core published claims (no GPU required, ~5 min)
make verify        # or: python scripts/verify_all_claims.py
```

If `make verify` runs and reports the probe/ablation claims, your setup works. 🎉

> Many contributions (docs, the website, data validation, analysis, the contributor
> experience) need **no GPU and no model API keys at all**.

---

## 3. Pick an issue

Every piece of work lives as a [GitHub issue](https://github.com/justinshenk/temporal-awareness/issues).
Issues are labeled so you can find one that fits you:

| Label group | What it tells you |
|---|---|
| `good first issue` | Scoped and mentored — **start here**. |
| `track:A-probe-infra` / `track:B-experiment` | Shared infrastructure vs a standalone experiment. |
| `thrust:foundations` / `mechanisms` / `robustness` / `theory` | The research area. |
| `difficulty:intermediate` / `difficulty:research` | How open-ended it is (no label = beginner-friendly). |
| `needs-dataset` | Blocked on building a dataset first — a great contribution in itself. |

See [`docs/RESEARCH_PROGRAM.md`](RESEARCH_PROGRAM.md) for how Tracks and Thrusts fit together.

**To claim an issue:** comment `I'd like to work on this` (or use the "Claim this" button on
the project website). A maintainer will assign you. Don't worry about being "qualified" — say
where you're at and we'll help you scope it.

---

## 4. Make your change

```bash
git checkout -b your-name/short-description

# ... make your change ...

ruff check .          # lint
pytest                # tests (use -m "not slow" to skip GPU/slow tests)
```

House rules (see [`CLAUDE.md`](../CLAUDE.md) for the full version):

- **Imports at the top** of the file, not inside functions.
- **Multi-word Python filenames** (`temporal_export.py`, not `export.py`).
- **No dead code** — no commented-out blocks or debug prints.
- **Don't touch the backend/pipeline** unless your issue is explicitly about it:
  `src/intertemporal/geoapp/**`, `scripts/intertemporal/**`, `src/activation_patching/**`.

---

## 5. Open your first pull request

```bash
git push -u origin your-name/short-description
```

Then open a PR on GitHub. The template will prompt you for what changed, how you tested it,
and to link the issue (`Closes #123`). Small PRs are welcome — it's fine to ship one focused
thing.

A maintainer will review. Expect friendly, specific feedback. **Asking questions in the PR is
encouraged** — that's how the project stays open.

---

## 6. Adding data

1. Add pairs to `data/raw/`.
2. Validate with `python scripts/data/validate_batch.py`.
3. Create splits with `python scripts/data/create_splits.py`.

---

## 7. Running experiments

The research workflows live in `scripts/`. Two common entry points:

```bash
# Train probe
python scripts/probes/train_temporal_probes_caa.py

# Evaluate
python scripts/probes/validate_dataset_split.py
```

---

## Glossary

- **Probe** — a small linear classifier trained on a model's internal activations to read off
  some property (here, short-term vs long-term).
- **Steering** — nudging a model's behavior by adding a direction to its activations.
- **Activation** — the internal numeric state a model produces as it processes text.
- **Horizon** — how far into the future a decision reaches. *Internal* horizon = what the
  activations imply; *stated* horizon = what the model says.
- **Activation patching** — swapping activations between two inputs to find which components
  *causally* drive a behavior.

---

By participating, you agree to abide by our
[Code of Conduct](../.github/CODE_OF_CONDUCT.md).
