"""Data-contract tests for the site export script.

These guard the contract the website depends on: the headline numbers must match the
verified results in ``results/`` (no drift), and every accuracy must be a probability.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "site" / "export_site_data.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("export_site_data", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def exported(tmp_path_factory):
    module = _load_module()
    out = tmp_path_factory.mktemp("site_public")
    module.export(out)
    data = {}
    for name in ("probe_separability", "claims", "figures"):
        data[name] = json.loads((out / "data" / f"{name}.json").read_text())
    data["_out"] = out
    return data


def test_probe_separability_peak_matches_verified_results(exported):
    sep = exported["probe_separability"]
    # Verified claim: temporal scope is linearly encoded, peaking at Layer 8 (92.5%).
    assert sep["peak_train"]["layer"] == 8
    assert sep["peak_train"]["accuracy"] == 0.925
    # Generalization: best held-out test accuracy is Layer 6 (84%).
    assert sep["peak_test"]["layer"] == 6
    assert sep["peak_test"]["accuracy"] == 0.84


def test_all_accuracies_are_probabilities(exported):
    for row in exported["probe_separability"]["layers"]:
        for key in ("train_accuracy", "test_accuracy"):
            value = row[key]
            if value is not None:
                assert 0.0 <= value <= 1.0, f"{key} out of range: {value}"


def test_claims_are_traceable_and_headline_number_present(exported):
    claims = exported["claims"]["claims"]
    assert len(claims) == 4
    # Every claim must cite a source file (integrity: no unsourced numbers on the site).
    for claim in claims:
        assert claim["source"], f"claim {claim['id']} has no source"
        assert claim["status"] in {"verified", "preliminary"}
    # The headline separability number is the verified 92.5%, derived from the CSV.
    assert claims[0]["value"] == "92.5%"
    assert "Layer 8" in claims[0]["metric"]


def test_figures_copied(exported):
    figs = exported["figures"]["figures"]
    assert figs, "expected at least one figure to be copied"
    for fig in figs:
        copied = exported["_out"] / "figures" / fig["file"]
        assert copied.exists(), f"figure not copied: {fig['file']}"
