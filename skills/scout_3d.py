"""Sovereign Scout3D skill powered by Crawl4AI for rich front-end extraction."""

from __future__ import annotations

import re
import urllib.request
from dataclasses import dataclass


@dataclass(slots=True)
class ScoutReport:
    """Extraction report for GSAP, Three.js, and scroll-physics artifacts."""

    url: str
    gsap_timelines: list[str]
    three_shaders: list[str]
    scroll_physics_signals: list[str]
    raw_length: int


class Scout3D:
    """Captures motion and rendering signatures from target URLs."""

    def __init__(self) -> None:
        self._crawler = self._build_crawler()

    def _build_crawler(self):
        try:
            from crawl4ai import Crawler

            return Crawler()
        except Exception:
            return None

    def _fetch(self, url: str) -> str:
        if self._crawler is not None:
            result = self._crawler.run(url=url)
            html = getattr(result, "html", "") or getattr(result, "content", "")
            if html:
                return html
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read().decode("utf-8", errors="ignore")

    def capture(self, url: str) -> ScoutReport:
        """Scrape a page and return reusable visual-motion fingerprints."""
        html = self._fetch(url)
        gsap_timelines = sorted(set(re.findall(r"gsap\.(?:timeline|to|fromTo)\([^)]*\)", html)))
        three_shaders = sorted(
            set(
                re.findall(
                    r"(?:vertexShader|fragmentShader)\s*:\s*[`\"]([\s\S]*?)[`\"]",
                    html,
                )
            )
        )
        scroll_physics_signals = sorted(
            set(
                re.findall(
                    r"(?:ScrollTrigger|locomotive-scroll|Lenis|scrollY|scroll-behavior)",
                    html,
                    flags=re.IGNORECASE,
                )
            )
        )
        return ScoutReport(
            url=url,
            gsap_timelines=gsap_timelines,
            three_shaders=three_shaders,
            scroll_physics_signals=scroll_physics_signals,
            raw_length=len(html),
        )
