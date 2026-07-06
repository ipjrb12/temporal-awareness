"""Content-accuracy guardrails for the public landing page.

The home page features research numbers, so this pins the grounded facts in place and
guards against re-introducing the unverified steering-correlation figure as a result.
"""

from pathlib import Path

INDEX = Path(__file__).resolve().parents[2] / "site" / "src" / "pages" / "index.astro"


def _source() -> str:
    return INDEX.read_text(encoding="utf-8")


def test_index_exists() -> None:
    assert INDEX.is_file(), f"missing landing page: {INDEX}"


def test_grounded_numbers_present() -> None:
    # Plain-language page keeps the two accessible headline accuracies.
    src = _source()
    for token in ["92.5", "99.2"]:
        assert token in src, f"expected grounded fact {token!r} on the landing page"


def test_candid_sections_present() -> None:
    src = _source().lower()
    assert "what we" in src, "expected a 'what we've done' section"
    assert "missing" in src or "open question" in src, "expected a candid 'missing' section"


def test_unverified_correlation_not_featured() -> None:
    # r=0.935 is labeled UNVERIFIED in-repo and its figure does not exist.
    assert "0.935" not in _source(), "must not present the unverified correlation as a result"
