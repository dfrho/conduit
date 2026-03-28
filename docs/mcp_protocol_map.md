# MCP Protocol Map

## What is MCP?

Model Context Protocol (MCP) is an open protocol for connecting LLM hosts (clients) to external capability providers (servers). It standardises how a model discovers and calls tools, reads resources, and samples from prompts — across any transport.

---

## Core Primitives

| Primitive    | Direction        | Description |
|--------------|------------------|-------------|
| **Tool**     | Client → Server  | A callable function with a JSON schema. The model invokes it; the server executes it and returns structured output. |
| **Resource** | Client → Server  | A URI-addressed read-only data source (e.g. `catalog://signal-sources`). Clients fetch it; servers expose it. |
| **Prompt**   | Client → Server  | A named, parameterised prompt template stored on the server. |
| **Sampling** | Server → Client  | A server-initiated request for the client's LLM to complete a prompt (reverse call). |

---

## Message Flow

```
Host (LLM app)
  └─ MCP Client
        │  initialize / list_tools / list_resources
        │─────────────────────────────────────────▶  MCP Server
        │
        │  tools/call  { name, arguments }
        │─────────────────────────────────────────▶
        │                     { content[], isError? }
        │◀─────────────────────────────────────────
        │
        │  resources/read  { uri }
        │─────────────────────────────────────────▶
        │                     { contents[] }
        │◀─────────────────────────────────────────
```

---

## Schema & Validation

- Tool inputs are declared as JSON Schema (or Pydantic / Zod models that compile to JSON Schema).
- The SDK validates arguments before the handler is called.
- Handlers return `{ content: [{ type, text }], isError? }` in the wire format; `FastMCP` wraps Python return values automatically.

---

## Transports

| Transport | Use case |
|-----------|----------|
| **stdio** | Local process — server is a child process, client writes to stdin / reads stdout. Default for CLI tooling. |
| **SSE**   | HTTP-based streaming — server runs as a web service. Used for remote / multi-client deployments. |

Conduit uses **stdio** for local development and eval runs.

---

## Lifecycle

1. **initialize** — capability negotiation (protocol version, feature flags)
2. **list_tools / list_resources / list_prompts** — discovery
3. **tools/call** or **resources/read** — normal operation
4. **shutdown** — graceful teardown (process exit on stdio)

---

## Error Model

MCP distinguishes two error layers:

| Layer | Mechanism | Example |
|-------|-----------|---------|
| Protocol error | JSON-RPC `error` object | Method not found, invalid params |
| Tool error | `isError: true` in content | `not_found`, `invalid_input` |

Conduit uses the **tool error** layer with a structured payload `{ error, message }` so callers can branch on error codes without parsing free text.
