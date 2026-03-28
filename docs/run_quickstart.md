# Running the Conduit MCP Server

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

---

## Start the server (stdio transport)

```bash
cd server-mcp
uv run conduit-server
# → Conduit MCP server running on stdio
```

---

## Inspect with the MCP dev UI

The `mcp` CLI ships an interactive inspector (runs in your browser):

```bash
cd server-mcp
uv run mcp dev conduit/server.py
# Opens http://localhost:5173 — lists tools, resources, lets you call them live
```

---

## Smoke-test via mcp CLI

```bash
# List tools
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' \
  | uv run conduit-server

# Call lookup_company
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"lookup_company","arguments":{"domain":"brightloop.io"}}}' \
  | uv run conduit-server

# Fetch the signal-sources resource
echo '{"jsonrpc":"2.0","id":3,"method":"resources/read","params":{"uri":"catalog://signal-sources"}}' \
  | uv run conduit-server
```

> Note: the `initialize` handshake is required before any other call in a real client session; the raw JSON examples above skip it for brevity.

---

## Run the Python quickstart reference server

The official MCP quickstart weather server (Python) lives at:
`modelcontextprotocol/quickstart-resources` → `weather-server-python/`

```bash
# Clone (one-time)
git clone https://github.com/modelcontextprotocol/quickstart-resources.git /tmp/mcp-quickstart

cd /tmp/mcp-quickstart/weather-server-python
uv run mcp dev weather.py
```

This exposes a `get-alerts` and `get-forecast` tool over stdio — the same
transport and lifecycle that Conduit uses.

---

## Project layout (post-migration)

```
server-mcp/
  fixtures/
    companies.json          # 5 firmographic records
    intent_signals.json     # intent signal data keyed by entity_id
  conduit/
    __init__.py
    server.py               # FastMCP server — tools + resource
  pyproject.toml            # uv project manifest
  uv.lock
```
