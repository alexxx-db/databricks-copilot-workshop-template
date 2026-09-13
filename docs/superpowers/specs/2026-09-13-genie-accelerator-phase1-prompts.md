# Genie Accelerator Track — Phase 1: Deck-Sized Prompt Drafts + Validation Runbook

**Status:** Phase 1 (spike). Draft prompts for live Genie Code validation — *not yet* encoded into
the section `.md` / `.genie-code.md` files (that is Phase 2).
**Date:** 2026-09-13
**Companion to:** `2026-09-13-genie-accelerator-track-design.md` (§4 step list, §5 prompt contract).
**Source of the prompt text:** "Genie in a Bottle" deck, Exercises 1–3 (slides 11a, 14a, 17a, 36).
We keep the deck's **chunking and wording** and add only: (a) read the context spine first,
(b) structured `catalog.schema`, (c) the two BYO-context lanes, (d) the Measures-Analysis gate.

---

## Conventions (apply to every prompt)

**Variables** (filled app-side before the prompt is copied, so Genie Code receives literal names):
- `{chapter_3_lakehouse_catalog}` / `{chapter_3_lakehouse_schema}` — the structured schema location
  captured via the app's `LakehouseParams` panel (§3 of the design spec). Shown below as
  `<catalog>.<schema>` for readability.
- `{use_case_title}` / `{function}` — from the selected use case / PRD.

**Context spine reads (the first line of every core prompt):**
> Read `docs/design_prd.md`, `docs/genie_brief.md`, and `.vibecoding-state.md` first. Reuse what
> they already answer; don't re-ask it.

**The fixed three-beat shape (§5 contract):** Elicit → Propose → **STOP for approval** → Build.
The deck's own rule, carried through every step: *"Ask for findings before artifacts. Have Genie
Code explain what it plans to do, review the plan, then approve."*

**Deck behavioral nudge (keep verbatim where it applies):** *"If Genie Code describes a Metric View
without creating it, reply: 'Create the Metric View now, do not just describe it.'"*

---

## Chapter: Discover

### Step 1 — Locate Data & Bring Context  *(new; app-led + thin GC prompt)*

**Leans on:** app `LakehouseParams` (structured input) + FM-API attachment ingestion
(`useCaseBuilderStream` / `processMetadataCsvStream`); Faker (synthetic branch).
**Gate:** `catalog.schema` saved to session `LakehouseParams` (or synthetic branch chosen);
`design_prd.md` read; `docs/genie_brief.md` seeded from PRD + any attachments.

*App-side, before the prompt:* pick `catalog.schema` (or toggle "No data → generate synthetic");
optionally attach an Excel glossary / a PDF / a dashboard screenshot. Then copy:

```
Read docs/design_prd.md first — reuse its User Journeys and High-Level Data Entities; don't
re-ask what it already answers.

My data for <function> is in <catalog>.<schema>. (If I said I have none, offer to generate
realistic sample data for <function>, tell me the tradeoff, and only generate it if I say yes.)

I've attached my current definitions (an Excel glossary / a dashboard export). Extract every
measure name, definition, and field alias you can from them.

Start docs/genie_brief.md from the PRD + attachments: function, candidate measures, and the
questions my users actually ask. Do NOT profile deeply or build anything yet — show me the
seeded brief so I can correct it.
```

**Golden transcript should show:** agent reads the PRD, echoes the confirmed `catalog.schema`,
pulls candidate definitions from the attachment, writes a first-pass `genie_brief.md`, and stops.

---

### Step 2 — Profile Schema  *(deck Ex1 · "Profile Your Schema", slide 11a)*

**Leans on:** native schema analysis. **Gate:** ERD produced; schema-supportability of each
candidate measure noted in the brief.

```
Read docs/genie_brief.md and .vibecoding-state.md first.

@<catalog>.<schema> holds the tables behind our <function> reporting.

Review this schema and report back on:
- What each table contains and its grain
- How the tables join, and any primary or foreign key candidates
- Which columns carry business meaning that is not obvious from the column name
- Which of the candidate measures in the brief the schema can support today

Produce an ERD. Do not create anything yet. Report your findings so I can review them, and note
any measure the schema cannot support yet.
```

**Golden transcript should show:** per-table grain, join/PK-FK candidates, "surprising column"
callouts, an ERD, and an explicit can/can't-support verdict per candidate measure — no assets
created.

---

### Step 3 — Measures Analysis  *(new gate; deck Ex1 · "Build Your Measure Inventory")*

**Leans on:** FM-API pre-fill from Step 2 profile + PRD + attachments. **Gate:** reviewed measures
table in `genie_brief.md`; ≤5 measures each with definition + source-of-truth + grain + owner;
conflicts written; **user signs off before ANY Metric View YAML.**

```
Read docs/genie_brief.md (profile + candidates) first.

Draft my measure inventory as a table with exactly these columns:
  Measure | Current definition (one sentence) | Source of truth (table.column or file) | Grain | Owner (a named person) | Conflict

Rules:
- Stop at five measures. Depth beats coverage — two well-governed measures beat fifteen half-
  governed ones.
- Name the source of truth as the actual table/column (or the file, if it came from an attachment).
- If two teams would define a measure differently, write BOTH in the Conflict column — the conflict
  is the finding, not a blocker.
- Mark any measure with no named owner as "unowned". No owner, no Metric View.

Pre-fill every cell you can from the brief and my attachments; leave a clear "?" where you need me.
Then STOP and show me the table. Do NOT write any Metric View YAML until I sign off on it.
```

**Golden transcript should show:** a filled inventory table, at least one conflict surfaced, unowned
rows flagged, and an explicit "waiting for your sign-off before authoring" stop. **This is the gate
the whole revision hinges on — no YAML appears in this transcript.**

---

## Chapter: Semantic (Metric Views)

### Step 4 — Draft the Metric View  *(deck Ex2 · prompt 1, slide 14a; + `/importBI` Path A)*

**Leans on:** native `using-metric-views`; **Path A:** Genie Code native `/importBI`.
**Gate:** each *approved* measure → 1 Metric View live; `MEASURE()` query returns; non-additive
flagged.

> **Path A (BYO, if you have a Tableau/PBI file):** run `/importBI` in Genie Code and upload your
> `.twb`, `.twbx`, or `.pbit`. Review — do **not** promote every Metric View the import produces;
> keep only the one covering your signed-off inventory. Then continue at Step 5.

**Path B — author from the signed-off inventory:**

```
Read docs/genie_brief.md (the signed-off measure inventory) first. Use only the measures I approved.

@<catalog>.<schema> holds the tables behind our <function> reporting.

Our business has agreed these measure definitions:
  <measure 1>: <one-sentence definition>
  <measure 2>: <one-sentence definition>

Work out which tables, joins, and grain each measure needs. Show me what the Metric View YAML would
look like, including dimensions people would want to slice by.

Do not save anything yet. Explain why you chose each grain, and flag any measure that is
non-additive.
```

When the YAML matches the inventory:

```
Create this Metric View as @<catalog>.<schema>.<metric_view>. Use business-friendly display names,
not column names.
```

> If Genie Code describes a Metric View without creating it, reply: *"Create the Metric View now, do
> not just describe it."*

**Golden transcript should show:** grain justified per measure, non-additive measures flagged,
YAML reviewed *before* creation, then a live Metric View; a `SELECT MEASURE(...) ... GROUP BY ALL`
returns a number.

---

### Step 5 — Add Synonyms  *(deck Ex2 · prompt 2, slide 14a)*

**Leans on:** native `using-metric-views`. **Gate:** ≥3 synonyms per measure/key dimension.

```
For the Metric View @<catalog>.<schema>.<metric_view>, add synonyms to every measure and dimension.

Include, for each one: the formal name, any acronym, the informal phrasing people in <function>
actually use, and any legacy name from our old reporting.

Show me the updated YAML before saving.

---
If I imported from a BI file, also pull the original field aliases from the imported workbook and
add them as synonyms.
```

**Golden transcript should show:** synonyms spanning acronym + informal + legacy for each measure;
BI field aliases folded in when Path A was used; YAML reviewed before save.

---

### Step 6 — Add Verified Queries  *(deck Ex2 · prompt 3, slide 14a)*

**Leans on:** native SQL. **Gate:** verified example queries attached; each returns; each shows the
correct filter + `MEASURE()` wrapping.

```
Add verified queries to @<catalog>.<schema>.<metric_view> for the two or three questions our
<function> users ask most often (pull them from the brief).

Each should show the correct filter and MEASURE() wrapping. These are the queries Genie should run
rather than reason out from scratch, so make them exact.

Show me each before saving.
```

**Golden transcript should show:** 2–3 verified queries, each with explicit filter + `MEASURE()`,
each executed once to prove it returns.

---

## Chapter: Agent (Genie Code path)

> The deck builds the agent in **Workbench** (Create Agent + Auto-Optimize). Our track runs on
> **Genie Code**, which the deck explicitly sanctions as the conversational fallback: *"If Workbench
> is unavailable, Genie Code can create and curate an agent conversationally."* Steps 7–10 use the
> Genie Code / MCP path (`manage_genie` create → curate → benchmark). Workbench Auto-Optimize is
> surfaced in "how it works" as the richer alternative.

### Step 7 — Describe the Agent  *(deck Ex3 · prompt 1, slide 17a)*

**Leans on:** partial native + `serialized_space` contract (existing export/import skill).
**Gate:** space scaffold with description; the Metric View attached under
`data_sources.metric_views`; `sql_functions` per TVF.

```
Read docs/genie_brief.md and .vibecoding-state.md first.

Create a Genie space for <function>. This agent answers questions about <what my team reviews> for
<function>. Its users are <who will ask>, and they typically ask about <two or three topics from the
brief>.

Attach @<catalog>.<schema>.<metric_view> as the data source. It should always use our governed
Metric View rather than querying raw tables.

Show me the space's serialized config before you create it.
```

**Golden transcript should show:** the Metric View placed under `data_sources.metric_views` (not as
a bare table), a plain-language scope, config reviewed before creation, then a live space id captured
to `.vibecoding-state.md`.

---

### Step 8 — Author Instructions  *(deck Ex3 · prompt 2, slide 17a)*

**Leans on:** native. **Gate:** instructions ≤20 lines; a preferred-source rule and an explicit
scope boundary present; no contradictions.

```
Add these instructions to the Genie space. Keep them lean — they load on every turn.

For any metric in scope, query the Metric View using MEASURE(). Do not re-derive metrics from raw
fact tables.

Scope: <what this agent covers>. Do not answer questions about <what it does not cover>.

Show me the final instruction block and cut anything that isn't load-bearing.
```

**Golden transcript should show:** short, rule-shaped instructions (not prose), a MEASURE()
preferred-source rule, a scope boundary, and the agent trimming non-load-bearing lines.

---

### Step 9 — Draft Benchmarks  *(deck Ex3 · prompt 3 + Optimize "Add Benchmarks", slides 17a/36)*

**Leans on:** partial native + benchmark-generation prompt. **Gate:** ≥10 benchmarks with expected
SQL; the space runs a real question correctly. **Expected answers are the user's to verify.**

```
Based on the Metric View attached to this space, suggest 15 benchmark questions a <function> user
would ask — from simple single-measure lookups to comparisons across time and dimensions. Add them
as benchmarks with expected SQL (correct filter + MEASURE() wrapping).

Then STOP: the generated QUESTIONS are a starting point, but the generated ANSWERS are a guess. I
will correct the expected answer on each before we treat any as validated. A benchmark set validated
against itself scores well and means nothing.
```

**Golden transcript should show:** ≥10–15 benchmarks with expected SQL, an explicit "verify these
answers yourself" stop, and at least one real question answered correctly by the live space.

---

## Chapter: Validate

### Step 10 — Validate & Iterate  *(deck Ex3 Optimize "Run Benchmarks" + Part 7 failure→fix)*

**Leans on:** native + optimize. **Gate:** benchmarks run; each failure triaged to a specific
curation action (failure→fix table); accuracy reported (target is *guidance*, ~85%, per §11 Q5 — not
a hard gate).

```
Run all benchmarks against this Genie space and report the pass rate. For each failing or
needs-review benchmark, diagnose the root cause and map it to ONE curation fix using this table:

  Right Page/measure not found  → add synonyms   (most common)
  Wrong source found            → tighten scope in instructions
  Outdated pattern used         → mark the asset deprecated
  Critical filter missed        → add it to the instructions
  Tables joined wrongly         → add a join hint / verified query

Apply the targeted fixes, re-run, and summarize what you changed with before/after pass rates. Aim
for ~85% on questions I verified — don't chase 100%.
```

**Golden transcript should show:** a baseline pass rate, a failure→fix mapping per failure, applied
fixes, and a re-run with an improved rate — with the fixes being *curation* (synonyms, scope,
instructions), not model changes.

---

## Chapter: Output

### Step 11 — Dashboard  *(beyond the deck's prompts; AI/BI on the Metric View)*

**Leans on:** AI/BI native. **Gate:** dashboard live; tiles query the Metric View (via `MEASURE()`),
not raw tables.

```
Create an AI/BI dashboard for <function> built on @<catalog>.<schema>.<metric_view>. Add tiles for
each governed measure (using MEASURE()) sliced by the key dimensions in the brief. Show me the tile
plan before building, then create it.
```

**Golden transcript should show:** tiles resolve through the Metric View's measures, a review-then-
build beat, and a live dashboard id captured to `.vibecoding-state.md`.

---

## Validation runbook (the Phase-1 spike)

Per the design spec §10 Phase 1: run these prompts **by hand on live Genie Code** against **two
reference schemas**, exercise **both BYO lanes**, prove the **Measures-Analysis gate**, and save the
resulting **Genie Code transcripts as golden references**.

**Matrix:**

| Run | Schema | Exercises | Must prove |
|---|---|---|---|
| A | **Clean-Gold** (a well-modeled `catalog.schema`) | Steps 1–11, Path B; BYO lane A (attach an Excel/CSV glossary at Step 1) | Full happy path end-to-end; brief seeded from attachment; gate holds |
| B | **Raw / needs-synthetic** (no usable data) | Step 1 synthetic toggle → Faker, then Steps 2–11; BYO lane B (`/importBI` a `.twbx`/`.pbit` at Step 4 Path A) | Adaptive synthetic branch; `/importBI` → Metric View; gate holds |

**Gate-specific checks (both runs):**
- **Measures-Analysis gate:** Step 3 transcript contains the reviewed table and **no** Metric View
  YAML; Step 4 only proceeds after an explicit sign-off line.
- **PRD spine:** Step 1 transcript shows the agent quoting `design_prd.md` User Journeys / Data
  Entities rather than re-asking them.
- **BYO lane A:** at least one measure definition in the brief is traceable to the uploaded file.
- **BYO lane B:** a Metric View originates from the `/importBI` payload, with its field aliases
  surviving as synonyms in Step 5.

**Acceptance:** each step reliably (a) triggers the interview, (b) produces its artifact, (c) passes
its gate — text iterated until true, transcripts saved under a Phase-1 evidence folder for Phase 2
to encode against.

---

## What I (the assistant) can do vs. what needs a human

I cannot *be* Genie Code (it is the in-workspace agent). Two ways to run the spike:

1. **You drive Genie Code** with the prompts above and paste back / save the transcripts. This
   produces the true golden references.
2. **I run a proxy validation via the Databricks MCP tools** (`get_table_stats_and_schema`,
   `execute_sql`, `manage_metric_views`, `manage_genie`, `ask_genie`) to prove the *operations* each
   prompt triggers are feasible on your live schema. This is not a Genie Code transcript, but it
   de-risks feasibility fast. **Read-only** for Steps 1–3 (profiling, ERD inputs, measure
   supportability); **asset-creating** for Steps 4–11 (Metric View, Genie space, benchmarks,
   dashboard) — so it needs your go-ahead on a target location.

To start either, I need three decisions from you (below).
