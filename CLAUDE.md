# Conduit Project Instructions

# 2-Week Compressed Sprint Plan

## MCP → LangSmith (Conduit FDE Training Track)

## What you’ll ship by Day 14

A single repo (or two repos with a monorepo wrapper) containing:

* **MCP Server (custom):** atomic tools + a “single tool call” macro-workflow (MCP abstraction)
* **MCP Client (CLI):** guarded agent loop + deterministic “eval mode”
* **LangSmith Integration:** end-to-end traces + dataset + evaluators + experiments
* **LangSmith MCP Server usage:** prompt/run/project ops via MCP
* **Interview Kit:** 5-minute demo script, architecture diagram, runbook, and “golden traces”

**Target audience:** forward-deployed engineer interview. Emphasis on reliability, fast iteration, measurable quality, and repeatable workflows.

---

# Sprint Rules (Keep You Fast)

* Every day ends with a **concrete artifact committed to git**.
* **No gold-plating:** prioritize demoable behavior + instrumentation over perfect modeling.
* **Determinism first:** mock data + fixtures early so evals are stable.
* **One-liners:** every major workflow should be runnable via a single command.

---

# Repo Structure (Recommended)

```
/ (root)
  /server-mcp/              # your custom MCP server
  /client-cli/              # your MCP client “agent”
  /eval/                    # datasets, evaluators, experiment runner
  /docs/                    # diagrams, runbooks, demo script
  Makefile (or package scripts)
```

---

# Week 1 — MCP Fluency + “Single Tool Call” Abstraction

## Day 1 — Boot + Baseline MCP Understanding

### Checkpoint

You can run the `modelcontextprotocol/quickstart-resources` example server and client end-to-end.

### Tasks

* Clone `modelcontextprotocol/quickstart-resources`
* Run at least one example (server + client)
* Write a short **protocol map**

### Deliverables

* `docs/mcp_protocol_map.md`
  *(tools vs resources, schemas, transport, lifecycle)*

* `docs/run_quickstart.md`
  *(exact commands to run baseline)*

---

## Day 2 — Build Your Own MCP Server Skeleton (Atomic Tools)

### Checkpoint

Your custom MCP server runs and exposes **2–3 tools with schema validation**.

### Tasks

Create `server-mcp/` using quickstart patterns.

Implement two tools (mock/fixture backed):

```
lookup_company({domain|name}) -> firmographics
get_intent_signals({entity_id, window}) -> signals[]
```

### Deliverables

* runnable `server-mcp/`
* `server-mcp/fixtures/*.json`
* `docs/tool_schemas.md` (inputs/outputs + examples)

---

## Day 3 — Add a Resource + Structured Errors

### Checkpoint

Server supports **at least one resource** and returns **structured errors**.

### Tasks

Add a resource:

```
/schemas/intent-signal
or
/catalog/signal-sources
```

Add error taxonomy:

```
invalid_input
not_found
rate_limited
provider_down
internal_error
```

Add timeouts + retry helper.

### Deliverables

* `docs/error_contract.md`
* `server-mcp/src/errors.ts | py`
* `client-cli` smoke test proving:

  * resource fetch
  * error case

---

## Day 4 — Reliability Hardening

### Checkpoint

You can simulate failures and show **graceful degradation**.

### Tasks

Add:

* caching layer for `get_intent_signals`
* tool budgets
* idempotency key support (stub acceptable)

### Deliverables

`docs/reliability.md`

Demo script:

```
scripts/demo_failures.sh
```

Demonstrates:

* cache hit / miss
* rate limit → backoff
* provider down → fallback

---

## Day 5 — Build the “Single Tool Call” Macro Workflow

### Checkpoint

One tool orchestrates multiple steps and returns a full workflow output.

### Macro Tool

```
icp_workflow_from_crm(
  {crm_sample, goal, constraints}
)
  -> {
       icp,
       audience,
       ranked_accounts,
       rationale,
       audit
     }
```

Output includes:

```
rationale[]
audit.steps[]
```

### Deliverables

* macro tool implementation
* `docs/workflow_tool.md`
* `server-mcp/fixtures/crm_sample.json`

---

## Day 6 — Build an MCP Client CLI

### Checkpoint

CLI can run:

```
plan → tool calls → final response
```

### Client Features

* tool allowlist
* max tool calls
* deterministic eval mode

Planner rule example:

```
if request mentions "ICP/audience/rank"
    call macro tool
else
    call atomic tools
```

### Commands

```
run "<question>"
run --eval "<question>"
```

### Deliverables

* `client-cli/`
* `docs/client_design.md`

---

## Day 7 — Demo Packaging + “Golden” Scenarios

### Checkpoint

You have a **3-minute demo that works offline**.

### Golden Prompts

1️⃣ ICP extraction + audience generation
2️⃣ Account ranking with explanations
3️⃣ Failure case with fallback

### Deliverables

```
docs/demo_script_v1.md
eval/golden_cases.jsonl
eval/expected_outputs/
```

Command:

```
make demo
```

---

# Week 2 — LangSmith Tracing + Evaluation

## Day 8 — LangSmith Tracing (Client Side)

### Checkpoint

Every CLI run produces a **LangSmith trace**.

### Add tracing to

* top-level request
* planner decision
* tool calls

Metadata:

```
tool_name
cache_hit
latency_ms
retry_count
record_count
```

### Deliverables

```
docs/langsmith_tracing.md
docs/golden_traces.md
```

---

## Day 9 — Server-Side Tracing

### Checkpoint

Tool handlers emit spans for debugging.

### Tasks

* server-side tracing
* shared `request_id`
* macro tool step spans

### Deliverables

```
docs/trace_correlation.md
```

Write one **debug story**.

---

## Day 10 — Dataset + Evaluators

### Checkpoint

Run experiment on **20–40 examples**.

Dataset types:

* ICP inference
* audience creation
* ranking + reasoning
* edge cases

### Evaluators

* schema validation
* efficiency limits
* rationale quality
* optional LLM judge

### Deliverables

```
eval/dataset.jsonl
eval/evaluators/
scripts/run_experiment
```

---

## Day 11 — Prompt Iteration

### Checkpoint

Show measurable improvement between two versions.

Possible improvements:

* planner prompt
* rationale format
* tool selection rule
* caching policy

### Deliverables

```
docs/experiment_report_v1.md
```

Include **3 failures + fixes**.

---

## Day 12 — Add LangSmith MCP Server

Use:

```
langchain-ai/langsmith-mcp-server
```

### Operations Flow

```
list projects
fetch runs
fetch prompt
```

### Deliverables

```
docs/langsmith_mcp_ops.md
scripts/langsmith_ops_demo.sh
```

---

## Day 13 — One-Command Eval

### Checkpoint

Single command:

* runs evals
* logs to LangSmith
* prints leaderboard

Command:

```
make eval
```

### Deliverables

```
docs/runbook.md
scripts/eval_summary.py | ts
```

---

## Day 14 — Interview Packaging

### Checkpoint

Deliver a **5-minute walkthrough**.

Finalize:

* architecture diagram
* demo script
* production narrative

### Deliverables

```
docs/architecture_diagram.png
docs/demo_script_final.md
docs/interview_talking_points.md
```

Topics:

* decisions
* tradeoffs
* metrics
* production path

---

# Daily Timebox Guidance

* **2–3 hrs** build
* **30–60 min** documentation
* **15 min** demo rehearsal

---

# Definition of Done

By Day 14 you should be able to:

```
make demo
make eval
```

Capabilities:

1. Run MCP server + client + macro workflow
2. Produce LangSmith experiments
3. Query LangSmith via MCP server
4. Open 3 golden traces explaining outcomes

---

# Suggested Interview Flow (5 Minutes)

1️⃣ **Problem** — AI apps need external data + repeatable workflows
2️⃣ **Solution** — MCP server with atomic tools + macro abstraction
3️⃣ **Reliability** — budgets, retries, caching, structured errors
4️⃣ **Measurement** — LangSmith traces + dataset + evaluators
5️⃣ **Ops** — LangSmith MCP server for prompt/run management
6️⃣ **Outcome** — demo + evaluation report + golden traces
