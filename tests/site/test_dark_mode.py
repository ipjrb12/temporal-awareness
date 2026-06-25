"""Guardrails for the site's day/night (dark/light) theme.

These are source-text assertions (matching the rest of tests/site) that pin the
theming *mechanism* in place: a system-matching, user-toggleable, no-FOUC dark mode.
"""

from pathlib import Path

SITE = Path(__file__).resolve().parents[2] / "site"
TAILWIND = SITE / "tailwind.config.mjs"
GLOBAL_CSS = SITE / "src" / "styles" / "global.css"
BASE_LAYOUT = SITE / "src" / "layouts" / "BaseLayout.astro"


def _read(path: Path) -> str:
    assert path.is_file(), f"missing expected file: {path}"
    return path.read_text(encoding="utf-8")


def test_tailwind_dark_mode_is_class_strategy() -> None:
    src = _read(TAILWIND)
    assert "darkMode" in src, "tailwind config must opt into dark mode"
    # class strategy lets us drive the theme from a single <html class="dark">.
    assert '"class"' in src or "'class'" in src, "dark mode should use the class strategy"


def test_semantic_colors_are_css_variable_backed() -> None:
    src = _read(TAILWIND)
    # The bulk of the site re-themes because paper/ink ride CSS variables.
    for token in ["--color-paper", "--color-ink", "--color-surface"]:
        assert token in src, f"expected semantic token {token!r} wired to a CSS variable"


def test_dark_palette_defined_in_global_css() -> None:
    src = _read(GLOBAL_CSS)
    assert "html.dark" in src or ".dark" in src, "expected a dark palette selector"
    assert "color-scheme: dark" in src, "dark mode should set color-scheme: dark"
    assert "--color-paper" in src, "dark palette must override the paper variable"


def test_header_has_a_theme_toggle() -> None:
    src = _read(BASE_LAYOUT)
    assert 'id="theme-toggle"' in src, "expected a theme toggle control in the header"
    assert "aria-label" in src, "the theme toggle should be accessibly labeled"


def test_no_flash_inline_theme_script() -> None:
    src = _read(BASE_LAYOUT)
    # Must run before paint, so it has to be an un-bundled inline script.
    assert "is:inline" in src, "the initial-theme script must be inline to avoid FOUC"
    # System-matching + persistence + live system updates.
    assert "prefers-color-scheme" in src, "theme must default to the system preference"
    assert "localStorage" in src, "the user's explicit choice must be persisted"
    assert "matchMedia" in src, "should react to live system theme changes"
    assert "dark" in src, "theme script toggles the dark class"
