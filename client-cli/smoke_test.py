"""Day 3 smoke test — proves resource fetch + all error codes via the MCP client."""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_DIR = Path(__file__).parent.parent / "server-mcp"
SERVER_CMD = ["uv", "run", "--project", str(SERVER_DIR), "conduit-server"]

# ── Helpers ───────────────────────────────────────────────────────────────────

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
_results: list[tuple[str, bool]] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    status = PASS if condition else FAIL
    suffix = f"  ({detail})" if detail else ""
    print(f"  [{status}] {label}{suffix}")
    _results.append((label, condition))


# ── Test cases ────────────────────────────────────────────────────────────────


async def run_tests(session: ClientSession) -> None:
    await session.initialize()

    # ── Resource: catalog://signal-sources ───────────────────────────────────
    print("\nResource")
    resp = await session.read_resource("catalog://signal-sources")
    import json
    sources = json.loads(resp.contents[0].text)
    check("signal-sources returns 5 entries", len(sources) == 5, str(len(sources)))
    check("first source is web_search", sources[0]["source"] == "web_search")

    # ── Tool: lookup_company — success ────────────────────────────────────────
    print("\nlookup_company")
    r = await session.call_tool("lookup_company", {"domain": "brightloop.io"})
    body = json.loads(r.content[0].text)
    check("domain lookup succeeds", not r.isError)
    check("returns correct entity_id", body.get("entity_id") == "ent_002", body.get("entity_id"))

    r = await session.call_tool("lookup_company", {"name": "Acme Corp"})
    body = json.loads(r.content[0].text)
    check("name lookup succeeds", not r.isError)
    check("name lookup returns ent_001", body.get("entity_id") == "ent_001")

    # ── Tool: lookup_company — errors ─────────────────────────────────────────
    r = await session.call_tool("lookup_company", {})
    body = json.loads(r.content[0].text)
    check("empty args → invalid_input", body.get("error") == "invalid_input", body.get("error"))

    r = await session.call_tool("lookup_company", {"domain": "nope.xyz"})
    body = json.loads(r.content[0].text)
    check("unknown domain → not_found", body.get("error") == "not_found", body.get("error"))

    # ── Tool: get_intent_signals — success ────────────────────────────────────
    print("\nget_intent_signals")
    r = await session.call_tool("get_intent_signals", {"entity_id": "ent_002", "window": "30d"})
    body = json.loads(r.content[0].text)
    check("30d signals for ent_002", not r.isError)
    check("count == 3", body.get("count") == 3, str(body.get("count")))

    r = await session.call_tool("get_intent_signals", {"entity_id": "ent_003", "window": "7d"})
    body = json.loads(r.content[0].text)
    check("empty 7d signals for ent_003", body.get("count") == 0)

    # ── Tool: get_intent_signals — error ──────────────────────────────────────
    r = await session.call_tool("get_intent_signals", {"entity_id": "ent_999", "window": "7d"})
    body = json.loads(r.content[0].text)
    check("unknown entity → not_found", body.get("error") == "not_found", body.get("error"))


# ── Entrypoint ────────────────────────────────────────────────────────────────


async def main() -> None:
    params = StdioServerParameters(command=SERVER_CMD[0], args=SERVER_CMD[1:])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await run_tests(session)

    print(f"\n{'─'*40}")
    passed = sum(1 for _, ok in _results if ok)
    total = len(_results)
    print(f"Results: {passed}/{total} passed")
    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
