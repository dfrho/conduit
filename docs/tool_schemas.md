# Tool Schemas — Conduit MCP Server

## `lookup_company`

Look up firmographic data for a company by domain or name.

### Input

| Field    | Type   | Required | Description                        |
|----------|--------|----------|------------------------------------|
| `domain` | string | optional | Company domain, e.g. `acme-corp.com` |
| `name`   | string | optional | Company name, e.g. `Acme Corp`     |

At least one of `domain` or `name` must be provided. `domain` takes precedence.

### Output (success)

```json
{
  "entity_id": "ent_001",
  "name": "Acme Corp",
  "domain": "acme-corp.com",
  "industry": "Manufacturing",
  "sub_industry": "Industrial Equipment",
  "employee_count": 1200,
  "revenue_range": "$50M–$100M",
  "hq_country": "US",
  "hq_state": "OH",
  "hq_city": "Columbus",
  "founded_year": 1987,
  "technologies": ["Salesforce", "SAP", "Snowflake"],
  "funding_stage": "Private",
  "description": "..."
}
```

### Errors

| Code            | Condition                          |
|-----------------|------------------------------------|
| `invalid_input` | Neither `domain` nor `name` given  |
| `not_found`     | No matching company in data set    |

---

## `get_intent_signals`

Retrieve intent signals for a known company entity over a lookback window.

### Input

| Field       | Type               | Required | Description                              |
|-------------|--------------------|----------|------------------------------------------|
| `entity_id` | string             | yes      | From `lookup_company` output             |
| `window`    | `"7d"` \| `"30d"` | yes      | Lookback window                          |

### Output (success)

```json
{
  "entity_id": "ent_002",
  "window": "30d",
  "count": 3,
  "signals": [
    {
      "signal_id": "sig_002_001",
      "topic": "AI marketing attribution",
      "source": "web_search",
      "strength": 0.91,
      "timestamp": "2026-02-27T16:45:00Z",
      "metadata": {
        "keyword": "multi-touch attribution AI",
        "page_views": 27
      }
    }
  ]
}
```

### Signal sources

| Source                | Description                          |
|-----------------------|--------------------------------------|
| `web_search`          | Keyword search activity              |
| `content_consumption` | Whitepaper / case study downloads    |
| `job_posting`         | Open roles signaling tech investment |
| `review_site`         | G2 / Capterra category browsing      |
| `conference`          | Event attendance / booth scans       |

### Errors

| Code        | Condition                           |
|-------------|-------------------------------------|
| `not_found` | `entity_id` has no signal records   |

---

## Typical Call Sequence

```
lookup_company({ domain: "brightloop.io" })
  → { entity_id: "ent_002", ... }

get_intent_signals({ entity_id: "ent_002", window: "30d" })
  → { count: 3, signals: [...] }
```

## Fixture Coverage

| entity_id | Company           | 7d signals | 30d signals |
|-----------|-------------------|------------|-------------|
| ent_001   | Acme Corp         | 2          | 3           |
| ent_002   | BrightLoop        | 1          | 3           |
| ent_003   | GridForce Energy  | 0          | 2           |
| ent_004   | NovaMed Health    | 1          | 2           |
| ent_005   | StackPilot        | 1          | 2           |
