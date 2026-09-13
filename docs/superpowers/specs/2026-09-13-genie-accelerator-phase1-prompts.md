# Genie Accelerator Track — Phase 1: Deck-Sized Prompt Drafts + Validation Runbook

**Status:** Phase 1 (spike). Draft prompts for live Genie Code validation — *not yet* encoded into
the section `.md` / `.genie-code.md` files (that is Phase 2).
**Date:** 2026-09-13
**Companion to:** `2026-09-13-genie-accelerator-track-design.md` (§4 step list, §5 prompt contract).
**Source of the prompt text:** "Genie in a Bottle" deck, Exercises 1–3 (slides 11a, 14a, 17a, 36).
We keep the deck's **chunking and wording** and add only: (a) read the context spine first,
(b) structured `catalog.schema`, (c) the reasoning-surface allocation (**Type A/B/C**, design spec
§5.1), (d) **Genie Code file-add** as the primary BYO lane, and (e) the Measures-Analysis gate.

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

**Reasoning-surface legend (design spec §5.1):**
- **Type A — app-authored prompt** (`bypass_llm=false`): the section `system_prompt` instructs the
  app's FM API to *generate* a personalized, ready-to-paste prompt (the `prd_generation` pattern).
  For Type A steps below, we give **both** the section `system_prompt` *and* an example of the
  generated output.
- **Type B — template prompt** (`bypass_llm=true`): variable substitution only; the text is
  authored by us and copied verbatim. Genie Code does the reasoning.
- **Type C — data-grounded** (`bypass_llm=true` delivery): the prompt tells the user to **drop files
  into Genie Code** and reason on the real content — the primary BYO lane.

**Per-step type map:**

| Step | Type | `bypass_llm` |
|---|---|---|
| 1 Locate + BYO | A → C | false |
| 2 Profile | B | true |
| 3 Measures Analysis (gate) | A + C | false |
| 4 Draft MV (Path A `/importBI` = C) | B / C | true |
| 5 Synonyms (Metric View `synonyms:`) | B | true |
| 6 Verified queries (Genie space — Agent chapter, after Step 7) | B | true |
| 7 Describe · 8 Instructions · 9 Benchmarks | B (9 opt. A-assisted) | true |
| 10 Validate · 11 Dashboard | B | true |

> Steps annotated **A** are written out with their `system_prompt` + generated output below. **Every
> other step is Type B** (`bypass_llm=true`, Genie Code reasons) unless its heading says otherwise.

---

## Chapter: Discover

### Step 1 — Locate Data & Bring Context  *(Type A → C · `bypass_llm=false`)*

**Reasoning split:** the app FM API *generates* this prompt (Type A); Genie Code then reasons on the
real schema + any **files you drop in** (Type C).
**Leans on:** app `LakehouseParams` (structured input) + FM-API prompt generation; Genie Code
file-add; Faker (synthetic branch).
**Gate:** `catalog.schema` saved to session `LakehouseParams` (or synthetic branch chosen);
`design_prd.md` read; `docs/genie_brief.md` seeded from PRD + any dropped files.

**Section `system_prompt` — the instruction to the app's FM API (the meta-prompt):**

```
You are generating a prompt the user will paste into Genie Code. Output a single, ready-to-paste
prompt (no preamble) that makes Genie Code:
 1. Read docs/design_prd.md first and reuse its User Journeys + High-Level Data Entities.
 2. Confirm the data location {chapter_3_lakehouse_catalog}.{chapter_3_lakehouse_schema} — or, if the
    user chose the synthetic path, offer to generate realistic sample data for {function} and only
    do so on approval.
 3. Read any files the user dropped into the repo (Excel glossary, CSV, docs) and extract measure
    names, definitions, and field aliases from them.
 4. Seed docs/genie_brief.md from the PRD + those files, then STOP for review.
Personalize the wording to {use_case_title} / {function}. Do NOT invent measures — instruct Genie
Code to elicit anything the PRD and files don't cover.
```

*App-side, before this runs:* pick `catalog.schema` (or toggle "No data → synthetic"); **drop your
Excel/CSV/docs into Genie Code** (into the repo or via the context button).

**Example generated output (what the app emits for you to paste):**

```
Read docs/design_prd.md first — reuse its User Journeys and High-Level Data Entities; don't
re-ask what it already answers.

My data for <function> is in <catalog>.<schema>. (If I have none, offer to generate realistic
sample data for <function>, tell me the tradeoff, and only generate it if I say yes.)

Read the files I dropped into the repo (an Excel glossary / a dashboard export) and extract every
measure name, definition, and field alias you can from them.

Start docs/genie_brief.md from the PRD + those files: function, candidate measures, and the
questions my users actually ask. Do NOT profile deeply or build anything yet — show me the seeded
brief so I can correct it.
```

**Golden transcript(s) should show:** (a) *app artifact* — the generated prompt above; (b) *Genie
Code transcript* — the agent reads the PRD, echoes the confirmed `catalog.schema`, **reads the
dropped file**, writes a first-pass `genie_brief.md`, and stops.

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

### Step 3 — Measures Analysis  *(Type A + C · `bypass_llm=false`; the gate — deck Ex1 · "Build Your Measure Inventory")*

**Reasoning split:** the app FM API generates the *framing* prompt (Type A); Genie Code fills the
table from the real Step 2 profile + **dropped glossary** (Type C).
**Leans on:** app FM-API prompt generation; Genie Code reasoning on the Step 2 profile + dropped
files. **Gate:** reviewed measures table in `genie_brief.md`; ≤5 measures each with definition +
source-of-truth + grain + owner; conflicts written; **user signs off before ANY Metric View YAML.**

**Section `system_prompt` — the instruction to the app's FM API:**

```
You are generating a prompt the user will paste into Genie Code. Output a single ready-to-paste
prompt that makes Genie Code build a MEASURE INVENTORY from what it already has — the Step 2 profile
in docs/genie_brief.md plus any files the user dropped in — as a table with columns:
Measure | Current definition | Source of truth (table.column or file) | Grain | Owner | Conflict.
Enforce: stop at five measures; write BOTH definitions in Conflict when teams disagree; mark unowned
measures "unowned" (no owner, no Metric View); pre-fill from real data, leave "?" where it needs the
user. It must STOP and show the table, and must NOT write any Metric View YAML until the user signs
off. Personalize to {function}.
```

**Example generated output (paste into Genie Code):**

```
Read docs/genie_brief.md (the Step 2 profile + candidates) and any files I dropped in first.

Draft my measure inventory as a table with exactly these columns:
  Measure | Current definition (one sentence) | Source of truth (table.column or file) | Grain | Owner (a named person) | Conflict

Rules:
- Stop at five measures. Depth beats coverage — two well-governed measures beat fifteen half-
  governed ones.
- Name the source of truth as the actual table/column (or the dropped file it came from).
- If two teams would define a measure differently, write BOTH in the Conflict column — the conflict
  is the finding, not a blocker.
- Mark any measure with no named owner as "unowned". No owner, no Metric View.

Pre-fill every cell you can from the brief and my dropped files; leave a clear "?" where you need me.
Then STOP and show me the table. Do NOT write any Metric View YAML until I sign off on it.
```

**Golden transcript(s) should show:** (a) *app artifact* — the generated framing prompt; (b) *Genie
Code transcript* — a filled inventory table, at least one conflict surfaced, unowned rows flagged,
and an explicit "waiting for your sign-off before authoring" stop. **This is the gate the whole
revision hinges on — no YAML appears in this transcript.**

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

> **Snowflake gotcha (Layer-2 finding):** single-level joins (fact → one dimension) and their
> dimensions resolve cleanly. **Nested** (snowflake) joins *parse*, but referencing a deeply nested
> join's column in a dimension `expr` is finicky (`customer.c_mktsegment` did not resolve as the
> docs imply). For multi-hop dimensions (e.g. Region via `customer → nation → region`), prefer a
> **pre-joined source view** or keep joins single-level. `synonyms`/`display_name`/`format` require
> YAML **v1.1**.

**Golden transcript should show:** grain justified per measure, non-additive measures flagged,
YAML reviewed *before* creation, then a live Metric View; a `SELECT MEASURE(...) ... GROUP BY ALL`
returns a number.

---

### Step 5 — Add Synonyms  *(deck Ex2 · prompt 2, slide 14a)*

**Leans on:** native `using-metric-views` (Metric View `synonyms:` field). **Gate:** ≥3 synonyms per
measure/key dimension, written to the MV YAML (`synonyms:`).

> **Layer-2 confirmed:** `synonyms` **is** a Metric View YAML feature (v1.1, ≤10 per measure/field)
> — verified live by re-creating the MV with `synonyms:` on every measure/dimension. It is *also*
> honored by Genie/BI for term discovery, so synonyms belong **here, on the Metric View** (not only
> on the space). Only *verified queries* (Step 6) are Genie-space-only.

```
For the Metric View @<catalog>.<schema>.<metric_view>, add a `synonyms:` list (YAML v1.1) to every
measure and to each key dimension — up to 10 each.

Include, for each one: any acronym, the informal phrasing people in <function> actually use, and any
legacy name from our old reporting.

Show me the updated YAML before saving.

---
If I imported from a BI file, also pull the original field aliases from the imported workbook and
add them as synonyms.
```

**Golden transcript should show:** synonyms spanning acronym + informal + legacy for each measure;
BI field aliases folded in when Path A was used; YAML reviewed before save.

---

### Step 6 — Add Verified Queries → **moved to the Agent chapter**

> **Layer-2 finding:** verified/example queries are **not** a Metric View feature — they live on the
> **Genie space** (`instructions.example_question_sqls`), confirmed by the MV syntax reference (no
> such field) and the space's serialized structure. This beat therefore runs **after** the space
> exists (Step 7). See **Step 6 (relocated) — Add Verified Queries** in the Agent chapter below.

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

### Step 6 (relocated) — Add Verified Queries  *(Genie space; deck Ex2 · prompt 3)*

**Leans on:** Genie space `instructions.example_question_sqls` (**not** the Metric View). **Runs
after Step 7** — the space must exist first. **Gate:** 2–3 verified Q→SQL examples attached to the
*space*; each queries the governed Metric View via `MEASURE()`; each returns.

```
For my Genie space, add verified example queries (question → SQL) for the two or three questions our
<function> users ask most often (pull them from the brief).

Each SQL must query the governed Metric View via MEASURE() with the correct filters — these are the
answers Genie should reuse rather than reason from scratch, so make them exact.

Show me each question/SQL pair before saving them to the space.
```

**Golden transcript should show:** 2–3 example_question_sqls saved to the *space* (not the MV), each
`MEASURE()`-based, each executed once to prove it returns.

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
reference schemas**, exercise BYO context **both ways** (drop a file into Genie Code + `/importBI`),
prove the **Measures-Analysis gate**, and save the resulting **Genie Code transcripts as golden
references**. For the **Type A** steps (1 and 3), also save the **app-generated prompt** as a
separate artifact — two artifacts per Type A step.

**Matrix:**

| Run | Schema | Exercises | Must prove |
|---|---|---|---|
| A | **Clean-Gold** (a well-modeled `catalog.schema`) | Steps 1–11, Path B; BYO via file-add (**drop an Excel/CSV glossary into Genie Code** at Step 1) | Full happy path end-to-end; brief seeded from the dropped file; gate holds |
| B | **Raw / needs-synthetic** (no usable data) | Step 1 synthetic toggle → Faker, then Steps 2–11; BYO via `/importBI` (a `.twbx`/`.pbit` at Step 4 Path A) | Adaptive synthetic branch; `/importBI` → Metric View; gate holds |

**Gate-specific checks (both runs):**
- **Measures-Analysis gate:** Step 3 transcript contains the reviewed table and **no** Metric View
  YAML; Step 4 only proceeds after an explicit sign-off line.
- **PRD spine:** Step 1 transcript shows the agent quoting `design_prd.md` User Journeys / Data
  Entities rather than re-asking them.
- **Type A two-artifact capture:** for Steps 1 and 3, the app-generated prompt is saved *separately*
  from the Genie Code transcript, and the transcript shows Genie Code executing that generated text.
- **BYO file-add:** Genie Code reads the **dropped** file and at least one measure definition in the
  brief is traceable to it.
- **BYO `/importBI`:** a Metric View originates from the `/importBI` payload, with its field aliases
  surviving as synonyms in Step 5.

**Acceptance:** each step reliably (a) triggers the interview, (b) produces its artifact, (c) passes
its gate — text iterated until true, transcripts saved under a Phase-1 evidence folder for Phase 2
to encode against.

---

## Layer-2 validation results (live `samples.tpch` on `fevm-serverless`, 2026-09-13)

Proxy validation via CLI (`--profile fevm-serverless`); assets created in
`serverless_stable_6t92c3_catalog.genie_accel_phase1`:

- **Steps 1–3 (read-only):** schemas confirmed; gross `SUM(l_extendedprice)` = **1.147T** vs net
  `SUM(l_extendedprice*(1-l_discount))` = **1.090T** (~5% — the real Finance-vs-Sales-Ops conflict);
  AOV non-additive; on-time rate computable from `l_receiptdate` / `l_commitdate`. ✔
- **Step 4 (Metric View):** `order_revenue_metrics` created (single-level `orders` join); a
  `MEASURE()` query returned monthly gross / net / units / AOV / on-time. ✔
- **Step 4 gotcha:** nested (snowflake) join dimension referencing is finicky — prefer single-level
  joins or a pre-joined source view for multi-hop dims (Region / Market Segment).
- **Step 5 (synonyms):** ✔ MV re-created with `synonyms:` on every measure/dimension — **confirmed a
  Metric View v1.1 feature** (also honored by Genie/BI).
- **Step 6 (verified queries):** ✖ **not** a Metric View feature → Genie space
  `instructions.example_question_sqls` (relocated to the Agent chapter, runs after Step 7).
- **Steps 7–9 (space):** `databricks genie create-space` exists but requires a full
  `serialized_space` (the easy `table_identifiers` path is MCP-only); benchmarks have
  `databricks genie genie-create-eval-run` (Beta). Live space build deferred to **Layer 3** (real
  Genie Code) where the native `genie_space` skill authors the serialized contract.

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

---

## Appendix A — Clean-Gold worked example (`samples.tpch`)

Validated read-only on profile `fevm-serverless` (2026-09-13): the sample is reachable and is a
clean TPC-H star. Use this as **Run A** (clean-Gold). Function = **order & revenue reporting**.

**Schema (validated):**
- **Fact:** `samples.tpch.lineitem` — grain = one order *line*. Money columns:
  `l_extendedprice`, `l_discount`, `l_tax`, `l_quantity`. Ships: `l_shipdate`, `l_shipmode`,
  `l_returnflag`.
- **`samples.tpch.orders`** — grain = one *order* (`o_orderkey`). `o_totalprice`, `o_orderdate`,
  `o_orderpriority`, `o_orderstatus`, `o_custkey`.
- **`samples.tpch.customer`** — `c_custkey`, `c_mktsegment`, `c_nationkey`, `c_acctbal`.
- **Joins:** `lineitem.l_orderkey → orders.o_orderkey`; `orders.o_custkey → customer.c_custkey`;
  `customer.c_nationkey → nation.n_nationkey → region.r_regionkey`.

**Measures to use (with a deliberate conflict + a non-additive case for the gate):**

| Measure | Definition (one sentence) | Source of truth | Grain | Conflict |
|---|---|---|---|---|
| Revenue | **Net of line discount:** `SUM(l_extendedprice * (1 - l_discount))` | `lineitem` | line | **Sales-ops reports GROSS** `SUM(l_extendedprice)` (no discount). Two numbers, same name — write both. |
| Average Order Value | Net revenue ÷ distinct orders — **non-additive** (never average across periods) | `lineitem` + `orders` | order | — |
| Units Sold | `SUM(l_quantity)` | `lineitem` | line | — |

The **Revenue gross-vs-net** row is what Step 3's transcript must surface as a *conflict* (not
silently pick one); **Average Order Value** is what Step 4 must flag as non-additive and Step 6/8
must protect with `MEASURE()`.

**Filled Step 2 (Profile) — paste into Genie Code (tag `@samples.tpch` first):**

```
Read docs/genie_brief.md first.

@samples.tpch holds the tables behind our order & revenue reporting.

Review this schema and report back on:
- What each table contains and its grain (lineitem vs orders especially)
- How the tables join, and any primary/foreign key candidates
- Which columns carry business meaning not obvious from the name (e.g. l_returnflag, o_orderstatus)
- Which of these measures the schema can support today: Revenue, Average Order Value, Units Sold

Produce an ERD. Do not create anything yet. Report your findings so I can review them.
```

**Filled Step 3 (Measures Analysis gate) — paste next:**

```
Read docs/genie_brief.md (the profile) first.

Draft my measure inventory as a table: Measure | Current definition | Source of truth | Grain |
Owner | Conflict.

Seed it with: Revenue, Average Order Value, Units Sold. For Revenue, note that gross
(SUM(l_extendedprice)) and net (SUM(l_extendedprice*(1-l_discount))) both circulate — write BOTH in
the Conflict column; the conflict is the finding. Flag Average Order Value as non-additive. Mark any
measure I haven't named an owner for as "unowned".

STOP and show me the table. Do NOT write any Metric View YAML until I sign off.
```

**Then** Step 4 Path B drafts the Metric View for the two signed-off measures (Revenue net + Average
Order Value), with Average Order Value flagged non-additive — exactly the deck's "why `MEASURE()`
isn't optional" demonstration, on real numbers.

**Run B (raw/synthetic):** at Step 1 choose the synthetic toggle → Faker generates a small
`<catalog>.<schema>` for `<function>`; the remaining steps are identical. Exercise BYO via
`/importBI` here by running it on a Tableau/PBI file at Step 4 Path A.
