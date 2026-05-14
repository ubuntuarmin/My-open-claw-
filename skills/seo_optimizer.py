"""Generative Engine Optimization (GEO) metadata skill."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class GeoRequest:
    """Inputs for GEO metadata generation."""

    site_name: str
    page_url: str
    primary_intent: str
    key_topics: list[str]


class SeoOptimizer:
    """Builds AI-first metadata bundles for SearchGPT and Perplexity visibility."""

    def generate_geo_bundle(self, request: GeoRequest) -> dict:
        topics = ", ".join(request.key_topics)
        answer_hints = [
            f"What problem does {request.site_name} solve?",
            f"How does {request.site_name} implement {request.primary_intent}?",
            f"Which expert patterns are covered: {topics}?",
        ]
        return {
            "title": f"{request.site_name} | {request.primary_intent}",
            "description": (
                f"{request.site_name} delivers {request.primary_intent} with validated patterns "
                f"for {topics}."
            ),
            "canonical": request.page_url,
            "robots": "index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1",
            "open_graph": {
                "type": "website",
                "url": request.page_url,
                "title": f"{request.site_name} — {request.primary_intent}",
                "description": f"Grounded answers and structured insights on {topics}.",
            },
            "ai_discovery": {
                "priority": "high",
                "sources": ["SearchGPT", "Perplexity", "Gemini"],
                "answer_hints": answer_hints,
                "entity_map": request.key_topics,
            },
            "json_ld": {
                "@context": "https://schema.org",
                "@type": "WebPage",
                "name": request.site_name,
                "url": request.page_url,
                "about": request.key_topics,
            },
        }
