"""Playwright-based performance and accessibility sentry checks."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SentryResult:
    """Result from sentry test execution."""

    fps: float
    accessibility_violations: list[str]
    passed: bool


class SentryTest:
    """Verifies 60fps performance target and baseline accessibility semantics."""

    def run(self, url: str, duration_ms: int = 1200) -> SentryResult:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:  # pragma: no cover - optional dependency path
            raise RuntimeError(
                "Playwright is required for sentry checks. Install playwright and browser binaries."
            ) from exc

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(url, wait_until="networkidle")
            fps = float(
                page.evaluate(
                    """
                    async ({ duration }) => {
                      const frames = [];
                      const start = performance.now();
                      while (performance.now() - start < duration) {
                        await new Promise(requestAnimationFrame);
                        frames.push(performance.now());
                      }
                      if (frames.length < 2) return 0;
                      const elapsed = frames[frames.length - 1] - frames[0];
                      return (frames.length - 1) / (elapsed / 1000);
                    }
                    """,
                    {"duration": duration_ms},
                )
            )
            violations = page.evaluate(
                """
                () => {
                  const findings = [];
                  document.querySelectorAll('img').forEach((el) => {
                    if (!el.hasAttribute('alt')) {
                      findings.push(`Missing alt attribute: ${el.outerHTML.slice(0, 120)}`);
                      return;
                    }
                    const alt = el.getAttribute('alt') || '';
                    const isDecorative = el.getAttribute('role') === 'presentation' || el.getAttribute('aria-hidden') === 'true';
                    const hiddenByAncestor = !!el.closest('[aria-hidden=\"true\"]');
                    if (!isDecorative && !hiddenByAncestor && !alt.trim()) {
                      findings.push(`Non-decorative image with empty alt text: ${el.outerHTML.slice(0, 120)}`);
                    }
                  });
                  document.querySelectorAll('button:not([aria-label])').forEach((el) => {
                    if (!el.textContent?.trim()) {
                      findings.push(`Button missing label: ${el.outerHTML.slice(0, 120)}`);
                    }
                  });
                  return findings;
                }
                """
            )
            browser.close()

        passed = fps >= 60 and len(violations) == 0
        return SentryResult(fps=fps, accessibility_violations=violations, passed=passed)
