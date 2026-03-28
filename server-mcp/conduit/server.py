"""Conduit MCP server — firmographics + intent signals."""

import json
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP

from conduit.errors import INVALID_INPUT, NOT_FOUND, err

# ── Fixtures ─────────────────────────────────────────────────────────────────

_FIXTURES = Path(__file__).parent.parent / "fixtures"

with open(_FIXTURES / "companies.json") as f:
    COMPANIES: dict = json.load(f)

with open(_FIXTURES / "intent_signals.json") as f:
    INTENT_SIGNALS: dict = json.load(f)

# ── Server ────────────────────────────────────────────────────────────────────

mcp = FastMCP("conduit")

# ── Resource: /catalog/signal-sources ────────────────────────────────────────

SIGNAL_SOURCES = [
    {
        "source": "web_search",
        "description": "Keyword search activity captured from B2B intent networks.",
        "fields": ["keyword", "page_views"],
    },
    {
        "source": "content_consumption",
        "description": "Whitepaper and case study downloads from gated content hubs.",
        "fields": ["content_type", "title"],
    },
    {
        "source": "job_posting",
        "description": "Open roles that signal technology investment or capability build-out.",
        "fields": ["job_title", "platform"],
    },
    {
        "source": "review_site",
        "description": "Category browsing on G2, Capterra, and similar review sites.",
        "fields": ["site", "category"],
    },
    {
        "source": "conference",
        "description": "Event attendance and booth scans at industry conferences.",
        "fields": ["event", "booth_scan"],
    },
]


@mcp.resource("catalog://signal-sources")
def signal_sources() -> str:
    """Catalog of intent signal source types and their metadata fields."""
    return json.dumps(SIGNAL_SOURCES, indent=2)


# ── Tool: lookup_company ──────────────────────────────────────────────────────


@mcp.tool()
def lookup_company(domain: str = "", name: str = "") -> dict:
    """Look up firmographic data for a company by domain or name.

    Returns industry, size, location, tech stack, and funding stage.
    Provide at least one of domain or name; domain takes precedence.

    Args:
        domain: Company domain, e.g. "acme-corp.com"
        name:   Company name, e.g. "Acme Corp"
    """
    if not domain and not name:
        return err(INVALID_INPUT, "Provide at least one of: domain, name")

    result = None

    if domain:
        result = COMPANIES.get(domain.lower())

    if result is None and name:
        name_lower = name.lower()
        result = next(
            (c for c in COMPANIES.values() if c["name"].lower() == name_lower),
            None,
        )

    if result is None:
        target = f'domain "{domain}"' if domain else f'name "{name}"'
        return err(NOT_FOUND, f"No company found for {target}")

    return result


# ── Tool: get_intent_signals ──────────────────────────────────────────────────


@mcp.tool()
def get_intent_signals(
    entity_id: str,
    window: Literal["7d", "30d"],
) -> dict:
    """Retrieve intent signals for a company entity over a time window.

    Signals include topic, source, strength score, and metadata.

    Args:
        entity_id: Entity ID from lookup_company (e.g. "ent_001")
        window:    Lookback window — "7d" (7 days) or "30d" (30 days)
    """
    entity_signals = INTENT_SIGNALS.get(entity_id)

    if entity_signals is None:
        return err(NOT_FOUND, f'No signals found for entity_id "{entity_id}"')

    signals = entity_signals.get(window, [])
    return {"entity_id": entity_id, "window": window, "count": len(signals), "signals": signals}


# ── Entrypoint ────────────────────────────────────────────────────────────────


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
