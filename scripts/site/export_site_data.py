"""Export verified research results into static JSON for the public website.

Read-only with respect to the research pipeline: this script only *reads* artifacts
under ``results/`` and *writes* into the site's ``public/`` directory. It never touches
the backend, the pipeline, or the source results.

Run:
    uv run python scripts/site/export_site_data.py            # writes to site/public
    uv run python scripts/site/export_site_data.py --out DIR  # custom output dir
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS = REPO_ROOT / "results"

# Figures (already generated, checked into results/) surfaced on the "What we score" page.
FIGURE_MANIFEST = [
    {
        "name": "layer_accuracy",
        "file": "layer_accuracy.png",
        "caption": "Probe accuracy by layer (train vs test). The signal is readable "
        "from a single layer and peaks in the middle of the network.",
        "source": "results/figures/layer_accuracy.png",
    },
    {
        "name": "probe_validation_heatmap",
        "file": "probe_validation_heatmap.png",
        "caption": "Probe validation across layers — where temporal scope is most "
        "linearly separable.",
        "source": "results/figures/probe_validation_heatmap.png",
    },
    {
        "name": "ablation",
        "file": "ablation.png",
        "caption": "With temporal keywords removed, late layers still separate "
        "short- vs long-term — evidence of semantic (not lexical) encoding.",
        "source": "results/figures/ablation.png",
    },
]


def _read_layer_accuracy(csv_path: Path) -> dict[int, dict[str, float]]:
    """Return {layer: {accuracy, std, n_samples, n_features}} from a verified CSV."""
    rows: dict[int, dict[str, float]] = {}
    with csv_path.open() as fh:
        for row in csv.DictReader(fh):
            layer = int(row["layer"])
            rows[layer] = {
                "accuracy": round(float(row["cv_accuracy_mean"]), 4),
                "std": round(float(row["cv_accuracy_std"]), 4),
                "n_samples": int(row["n_samples"]),
                "n_features": int(row["n_features"]),
            }
    return rows


def _peak(rows: dict[int, dict[str, float]]) -> dict[str, float]:
    best_layer = max(rows, key=lambda layer: rows[layer]["accuracy"])
    return {"layer": best_layer, "accuracy": rows[best_layer]["accuracy"]}


def build_probe_separability() -> dict:
    """Card 1: 'Can we read time-horizon off the activations?' — from verified CSVs."""
    train = _read_layer_accuracy(RESULTS / "verified" / "full_train_results.csv")
    test = _read_layer_accuracy(RESULTS / "verified" / "full_test_results.csv")
    layers = sorted(set(train) | set(test))
    return {
        "model": "gpt2",
        "n_features": train[layers[0]]["n_features"],
        "layers": [
            {
                "layer": layer,
                "train_accuracy": train.get(layer, {}).get("accuracy"),
                "train_std": train.get(layer, {}).get("std"),
                "test_accuracy": test.get(layer, {}).get("accuracy"),
            }
            for layer in layers
        ],
        "peak_train": _peak(train),
        "peak_test": _peak(test),
        "source": "results/verified/full_train_results.csv, "
        "results/verified/full_test_results.csv",
    }


def build_claims(separability: dict) -> dict:
    """The published 'Main Claims' (results/README.md), with values tied to data."""
    pct = lambda x: f"{round(x * 100, 1):g}%"
    peak_train = separability["peak_train"]
    peak_test = separability["peak_test"]
    return {
        "claims": [
            {
                "id": 1,
                "claim": "Temporal scope is linearly encoded",
                "metric": f"Probe accuracy (Layer {peak_train['layer']})",
                "value": pct(peak_train["accuracy"]),
                "status": "verified",
                "source": "results/verified/full_train_results.csv",
            },
            {
                "id": 2,
                "claim": "Encoding generalizes to a held-out test set",
                "metric": f"Test accuracy (Layer {peak_test['layer']})",
                "value": pct(peak_test["accuracy"]),
                "status": "verified",
                "source": "results/verified/full_test_results.csv",
            },
            {
                "id": 3,
                "claim": "Steering moves the same features the probe detects",
                "metric": "Correlation (steering strength vs probe prediction)",
                "value": "r = 0.935",
                "status": "preliminary",
                "source": "results/README.md",
            },
            {
                "id": 4,
                "claim": "Late layers encode semantic, not lexical, features",
                "metric": "Ablation accuracy, L10-11 (temporal keywords removed)",
                "value": "100%",
                "status": "verified",
                "source": "results/README.md",
            },
        ]
    }


def copy_figures(out_dir: Path) -> dict:
    """Copy referenced figures into the site and return a manifest."""
    fig_out = out_dir / "figures"
    fig_out.mkdir(parents=True, exist_ok=True)
    available = []
    for fig in FIGURE_MANIFEST:
        src = RESULTS / "figures" / fig["file"]
        if src.exists():
            shutil.copy2(src, fig_out / fig["file"])
            available.append(fig)
    return {"figures": available}


def export(out_dir: Path) -> dict[str, Path]:
    """Write all site data artifacts. Returns {artifact_name: path}."""
    data_dir = out_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    separability = build_probe_separability()
    artifacts = {
        "probe_separability": separability,
        "claims": build_claims(separability),
        "figures": copy_figures(out_dir),
    }
    written: dict[str, Path] = {}
    for name, payload in artifacts.items():
        path = data_dir / f"{name}.json"
        path.write_text(json.dumps(payload, indent=2) + "\n")
        written[name] = path
    return written


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "site" / "public",
        help="Output directory (default: site/public).",
    )
    args = parser.parse_args(argv)
    written = export(args.out)
    for name, path in written.items():
        print(f"wrote {name:20s} -> {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
