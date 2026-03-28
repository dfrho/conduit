# Error Contract — Conduit MCP Server

## Error payload shape

All tool errors return a plain dict (not a raised exception) so the MCP
client receives them as tool content rather than a protocol-level fault:

```json
{ "error": "<code>", "message": "<human-readable detail>" }
```

The `error` field is always a stable machine-readable code. `message` is for
humans and may change; callers must branch on `error`, not `message`.

---

## Error taxonomy

| Code             | HTTP analogue | Meaning | Retryable? |
|------------------|---------------|---------|------------|
| `invalid_input`  | 400           | Required fields missing or mutually exclusive constraints violated. | No |
| `not_found`      | 404           | Entity ID, domain, or name has no record in the data set. | No |
| `rate_limited`   | 429           | Upstream provider has throttled the request. | Yes |
| `provider_down`  | 503           | Upstream data provider is unreachable or returned a 5xx. | Yes |
| `internal_error` | 500           | Unexpected error inside the tool handler. | No |

---

## Retry policy (`conduit.errors.with_retry`)

Only `rate_limited` and `provider_down` are retried automatically.

| Parameter      | Default | Description |
|----------------|---------|-------------|
| `max_attempts` | 3       | Total tries before returning the last error. |
| `base_delay`   | 0.5 s   | Initial back-off; doubles each attempt (exponential). |
| `timeout`      | 5.0 s   | Per-attempt `asyncio.wait_for` deadline. |

Back-off sequence: 0.5 s → 1.0 s → give up.

```python
from conduit.errors import with_retry

result = await with_retry(lambda: fetch_signals(entity_id, window))
```

---

## Tool-level error coverage

| Tool                | `invalid_input` | `not_found` | `rate_limited` | `provider_down` | `internal_error` |
|---------------------|:-:|:-:|:-:|:-:|:-:|
| `lookup_company`    | ✓ | ✓ | stub | stub | — |
| `get_intent_signals`| — | ✓ | stub | stub | — |

*stub* = error code is defined and retryable by the retry helper; not yet
triggered by fixture-backed handlers (will be wired when live providers are
added).

---

## MCP vs tool errors

| Layer | When used | Wire format |
|-------|-----------|-------------|
| Protocol error | Bad JSON-RPC, unknown method | `{"error": {"code": -32601, ...}}` |
| Tool error (this doc) | Business logic failures | `content[].text` with `{"error": ..., "message": ...}` |

Callers should check `isError` on the tool result first, then parse the
`error` field from the content text.
