# Genie Accelerator Track — Phase 1: Deck-Aligned Prompt Drafts + Validation Runbook

**Status:** Phase 1 (spike). Draft prompts for live Genie Code validation — *not yet* encoded into
the section `.md` / `.genie-code.md` files (that is Phase 2).
**Date:** 2026-09-13 (rewritten r7 — full re-alignment to the deck; see companion spec r7).
**Companion to:** `2026-09-13-genie-accelerator-track-design.md` (§4 step list, §5 prompt contract,
r7 finalized-alignment revision).
**Source of the prompt text:** the **"Genie in a Bottle" deck, Exercises 1–6** (slides 11a, 14a,
17a, 22a, 26a, and the Part-7 failure→fix table on slide 28). **The deck is the spine.** We keep the
deck's chunking and wording and add **only** the enhancement whitelist below.

**Enhancement whitelist (the ONLY sanctioned deviations from the deck):**
1. **Step 0 PRD (Type A)** + **`vibecoding-state`** — the context spine the deck lacks.
2. **Structured source+write input** — reuse the app's existing surfaces: `LakehouseParamsEditor`
   (source, per-session) + `GoldTableTargetEditor` (write target). **No new variables/pair** (see Conventions).
3. **BYO context** via Genie Code file-add + `/importBI` (both deck-sanctioned).
4. **Discover-don't-inject** Measures gate (matches the deck's Ex1 spirit; proven unprompted in `run-a`).
5. **Batched interview** (one numbered list of questions with pre-filled assumptions).
6. **Metric View corrections:** nested joins work / pre-joined recommended; idempotent `CREATE OR REPLACE`.
7. **Verified queries attach to the space** (the deck's Ex2 prompt-3 wording is loose — MVs have no
   `example_question_sqls`; the *draft* is discussed in Ex2, the *apply* happens in Ex3).
8. **Optional Activation tail** (dashboard → synced tables → Lakebase → App → DAB) — beyond the deck.

**What is NOT a deviation (deck fidelity restored in this rewrite):**
- **Ex3 optimize loop.** The deck loads benchmarks *with expected answers* and runs the optimizer.
  The fully-automatic **Workbench "Auto-Optimize" (GSO) job is Workbench-only — Genie Code cannot
  launch it.** The GC-native equivalent, which this track uses, is the **benchmark curation loop**:
  benchmarks-with-expected-SQL → run via the **Conversation API (`ask_genie`)** → diff → map each
  miss to the **5-mode fix table** → **append-only** fixes → **re-run** to **≥85%**. This is exactly
  the tooling in `data_product_accelerator/skills/semantic-layer/03-genie-space-patterns`
  (Rule 12 intake, Rule 17 append-only optimize, the regression-test template, Conversation-API
  validation). `run-a`'s optimize weakness was an *ad-hoc, unclosed* loop — fixed here.
- **Ex4 Domains + Pages and Ex5 Routing Page** are **core** chapters (were dropped; now restored),
  with explicit caveats: Pages is **Beta**, has **no public create/update API** (authored in the
  Discover UI with Genie Code assisting), and grounds **Genie One** (agent/GC integration is roadmap).

---

## Conventions (apply to every prompt)

**Variables** (filled app-side before the prompt is copied, so Genie Code receives literal names).
**No new runtime variables are introduced** — everything below maps onto tokens/surfaces the app
already has (confirmed against the app repo, 2026-09-13):
- `{source_catalog}` / `{source_schema}` — where the **existing data** lives (Step 1). May be
  **read-only** (e.g. `samples.tpch`). Shown below as `<source_catalog>.<source_schema>`. These are the
  app's existing **`{chapter_3_lakehouse_catalog}` / `{chapter_3_lakehouse_schema}`** ("Lakehouse Source
  Catalog/Schema"), captured via **`LakehouseParamsEditor`** (per-session overridable) — not new tokens.
- `{write_catalog}` / `{write_schema}` — the **writable target** where governed assets (Metric View,
  Genie space, dashboard) are created. **Distinct from the source** — Layer-3 proved the source is
  often read-only, so the build target is captured separately, never guessed by Genie Code. This is the
  app's existing **`{lakehouse_default_catalog}`** (write catalog) + the **`GoldTableTargetEditor`**
  schema/prefix — **not** a "second `LakehouseParams` pair" and **not** a new `lakehouse_default_schema`
  token. Shown as `<write_catalog>.<write_schema>`.
- `{metric_view}` — the Metric View name. **Not a variable** — **Genie Code suggests it** (app defaults
  the display from `{function}`, e.g. `order_revenue_metrics`) and writes the chosen name to state.
- `{use_case_title}` / `{function}` — from the selected use case / PRD.
- `{domain}` / `{subdomain_*}` — the discovery domain + subdomains authored in Ex4. **UI-first, not
  variables** — authored/selected in the Discover UI (a workshop domain may be pre-created; if so, use
  it). Shown in prompts as readable placeholders only.
- `{byo_glossary_file}` — **the user's own** definitions export (an Excel glossary, a CSV, a docs
  file, or a Tableau/PBI file). **Not a variable — uploaded directly** (chat drop / UC volume /
  `CsvUploadPanel` / `/importBI`). Optional; there is no fixture file — if the
  user has none, the BYO lines are skipped and Genie Code elicits definitions instead.

> **Historical note:** earlier drafts used a single `{chapter_3_lakehouse_catalog}.{schema}` for both
> read and write. Layer-3 (`run-a`) showed the source (`samples.tpch`) was read-only and the assets
> had to land in a separate writable schema — hence the `source` vs `write` split above.

**State wrapper (`vibecoding-state`, applied once per run — see design spec §3 spine):**
> Before Step 0, open the session: run the `vibecoding-state` bootstrap/`enter` so Genie Code
> resolves `artifact_root`, loads `client_context`, and creates/loads `.vibecoding-state.md`. Every
> core prompt reads `.vibecoding-state.md` first and writes its gate result back to it; the run ends
> with `vibecoding-state` `exit`. Capture the `.vibecoding-state.md` delta after each step as
> evidence (see the runbook).

**Context spine reads (the first line of every core prompt) — `design_prd.md` is the head of the spine:**
> Read `docs/design_prd.md`, `docs/genie_brief.md`, and `.vibecoding-state.md` first. Reuse what
> they already answer; don't re-ask it.
>
> **Where the PRD is read *directly* (not just via the brief):** the `design_prd.md` **User Journeys**
> and **personas** are load-bearing at **Step 1** (seed the brief), **Step 3** (which measures matter
> follows the journeys), **Step 6** (the agent's users + topics ARE the PRD personas/journeys), and
> **Step 9** (the benchmark questions are the journeys). Everywhere else the brief already carries the
> PRD forward, so those steps read `genie_brief.md` + `.vibecoding-state.md`. **Every core prompt still
> ends by recording its gate/artifact-id to `.vibecoding-state.md`** — that write-back is what
> maintains continuity across a multi-day run (see the State wrapper above).

**Navigation / surface-scoping (Genie Code — `skills/genie-code-environment` §1, §6c):**
> Genie Code **scopes its available tools to the page/asset you are currently on** — the same request
> succeeds on the right surface and returns "not in the allow-list" on the wrong one. **When a step
> creates or edits an asset, be on the matching page first.** Each affected step below carries an
> explicit *Navigation:* note. The load-bearing ones:
> - **Genie Space (Step 6):** created via the native `createAsset(assetType:"genie", …)` shell, then
>   populated with `PATCH /api/2.0/genie/spaces/{id}` — do this from a workspace/Genie surface, not a
>   bundle-editor page.
> - **AI/BI Dashboard (Step 15):** `createAsset(assetType:"dashboard")` then **auto-navigate**
>   `openAsset(...)` to the **dashboard canvas** — widget editing requires the canvas page; there is no
>   remote widget edit. Print the clickable dashboard link.
> - **Domains / Pages (Steps 11–13):** authored in the **Discover UI** — **domains + subdomains are
>   created in the UI directly (the preferred method; a workshop may pre-create the domain)**; Pages
>   have no public API and are authored in the Discover Page editor with Genie Code assisting (paste
>   the draft). Navigate to Catalog → Discover → your domain.
> - **DAB deploy (Step 17):** `bundle deploy` is pinned to the **bundle-editor page** of the bundle
>   root — open that folder's bundle editor before deploying. A "blocked"/`databricks.yml not found`
>   message is a **wrong-page signal, not a dead end**.
> A blocked capability is usually a wrong-surface signal: **navigate first, then retry** — don't
> conclude it's impossible or fall back to raw SQL.

**The fixed three-beat shape (§5 contract):** Elicit → Propose → **STOP for approval** → Build.
The deck's own rule, carried through every step: *"Ask for findings before artifacts. Have Genie
Code explain what it plans to do, review the plan, then approve."*

**Deck behavioral nudge (keep verbatim where it applies):** *"If Genie Code describes a Metric View
without creating it, reply: 'Create the Metric View now, do not just describe it.'"*

**Reasoning-surface legend (design spec §5.1):**
- **Type A — app-authored prompt** (`bypass_llm=false`): the section `system_prompt` instructs the
  app's FM API to *generate* a personalized, ready-to-paste prompt (the `prd_generation` pattern).
  **Only the PRD (Step 0) is Type A** — and its real source is the shipped section file, not this
  doc (see Step 0).
- **Type B — template prompt** (`bypass_llm=true`): variable substitution only; the text is
  authored by us and copied verbatim. Genie Code does the reasoning.
- **Type C — data-grounded** (`bypass_llm=true` delivery): the prompt tells the user to **drop files
  into Genie Code** and reason on the real content — the primary BYO lane.

> **Only Step 0 (PRD) is Type A.** Every core prompt below is a **static template**
> (`bypass_llm=true`): fixed deck text with `catalog.schema` / `function` / `{domain}` /
> `{byo_glossary_file}` substituted in, copied verbatim, and **Genie Code does all the domain
> reasoning** — including discovering conflicts. No prompt asserts a domain-specific finding.

**Step map (deck exercise → step → surface → binding skill):**

| Step | Deck | Chapter / surface | Type | Binds to |
|---|---|---|---|---|
| 0 PRD | — | Frame · App FM-API → GC | A | `apps_lakebase/prompts/sections/03-prd_generation.md` |
| 1 Locate + BYO | Ex1 | Discover · GC | C | `LakehouseParams`, file-add, Faker |
| 2 Profile | Ex1 / 11a | Discover · GC | B | native schema analysis |
| 3 Measures gate | Ex1 | Discover · GC | B→C | design spec §4 gate |
| 4 Draft Metric View | Ex2 / 14a | Metric View · GC | B/C | `semantic-layer/01-metric-views-patterns`, `/importBI` |
| 5 Synonyms | Ex2 / 14a | Metric View · GC | B | `semantic-layer/01-metric-views-patterns` |
| 6 Describe agent | Ex3 / 17a | Agent · GC | B | `semantic-layer/03-genie-space-patterns` |
| 7 Instructions | Ex3 / 17a | Agent · GC | B | `03-genie-space-patterns` (General Instructions ≤20 lines) |
| 8 Verified queries (on space) | Ex2 #3 (corrected) | Agent · GC | B | `03-genie-space-patterns`, `04-genie-space-export-import-api` |
| 9 Load benchmarks (expected SQL) | Ex3 / 17a + 36 | Agent · GC | B | `03-genie-space-patterns` Rule 12 |
| **10 Optimize (run → fix → re-run)** | Ex3 Optimize + Part 7 / 28 | Agent · GC | B | `03-genie-space-patterns` Rule 17 + regression template |
| 11 Domain + subdomains | Ex4 / 22a | Domain & Pages · **Discover UI (preferred)** | B | *(skill gap — Discover UI; GC assist optional)* |
| 12 Author Pages | Ex4 / 22a | Domain & Pages · Discover UI | B/C | *(skill gap)* |
| 13 Routing Page | Ex5 / 26a | Routing · Discover UI | B | *(skill gap)* |
| 14 Share | Ex6 | Share · everyone | — | — |
| 15 Dashboard *(optional tail)* | — | Activation · GC | B | AI/BI native |
| 16 Synced tables → Lakebase → App *(optional tail)* | — | Activation · GC | B | `databricks-lakebase`, `apps_lakebase` skills |
| 17 Productionize as DAB *(optional tail)* | — | Activation · GC | B | `databricks-asset-bundles` |

---

## Chapter: Frame

### Step 0 — PRD  *(Type A · `bypass_llm=false` · the ONLY app-generated prompt)*

**Do not hand-write this prompt.** It is generated by the app's FM API from the shipped section
file — **`apps_lakebase/prompts/sections/03-prd_generation.md`** (`## System Prompt` block) — using
the selected use case + `use_case_description`. For a faithful Phase-1 run, obtain the PRD prompt one
of two ways, and **save the emitted prompt verbatim** as the Step-0 evidence artifact:

1. **Via the app** — run the existing PRD step and copy the generated prompt (production path).
2. **Via a faithful mimic** — feed that section's `## System Prompt` + your use-case description to a
   Databricks serving endpoint (the same FM API the app calls) and capture the output. Use this only
   when the app UI isn't available; it must use the real section text, not an approximation.

Paste the emitted prompt into Genie Code; it writes `docs/design_prd.md`. Everything downstream reads
that file. (This is the single Type A beat — see the step map above.)

**Gate:** `docs/design_prd.md` exists with User Journeys + High-Level Data Entities; the
app-generated prompt is saved separately as evidence; the PRD gate is recorded in
`.vibecoding-state.md` (the `vibecoding-state` bootstrap/`enter` created the file just before this
step — see the State wrapper).

---

## Chapter: Discover  *(deck Exercise 1)*

### Step 1 — Locate Data & Bring Context  *(Type C · `bypass_llm=true` · static file-drop template)*

**Reasoning split:** static template (variable substitution only); **Genie Code** reasons on the
real schema + any **files you drop in**. The app does *not* generate this prompt.
**Leans on:** the app's existing **extract/upload/generate mode-tab pattern** (from Step 10
`bronze_table_metadata`) — reuse it here: **extract** = read existing tables via `LakehouseParamsEditor`
(source catalog/schema); **upload** = `CsvUploadPanel`; **generate** = "Design from PRD" = the
**synthetic / no-existing-data** branch (Faker). Plus Genie Code file-add for BYO definitions.
**Navigation:** none — pick the mode tab, then file-drop + reasoning; drop the glossary/BI export via
the context button, then run from any workspace surface.
**Gate:** `catalog.schema` saved to session `LakehouseParams` (or synthetic branch chosen);
`design_prd.md` read; `docs/genie_brief.md` seeded from PRD + any dropped files, gate recorded to
`.vibecoding-state.md`.

*App-side, before you copy:* pick `catalog.schema` (or toggle "No data → synthetic"); if you have
existing definitions, **drop `{byo_glossary_file}` into Genie Code** (into the repo or via the
context button). If you have none, delete the two BYO lines below — Genie Code will elicit instead.

**Template (copy verbatim; `<...>` are pre-filled app-side):**

```
Read docs/design_prd.md and .vibecoding-state.md first — reuse the PRD's User Journeys and
High-Level Data Entities; don't re-ask what they already answer.

My data for <function> is in <source_catalog>.<source_schema>. (If I have none, offer to generate
realistic sample data for <function>, tell me the tradeoff, and only generate it if I say yes.)

I've dropped my current definitions into the repo (<byo_glossary_file>). Read them and pull out
every measure name, definition, and field alias you can — cite which file each came from.

Start docs/genie_brief.md from the PRD + those files: function, candidate measures, and the
questions my users actually ask. If anything the PRD and files don't cover needs my input, collect
ALL of it into ONE numbered list of questions and ask me in a single batch — do not drip them one at
a time. Pre-fill your best assumption for each and mark it "(assumed — correct me)" so I can just fix
the ones that are wrong. Do NOT profile deeply or build anything yet — show me the seeded brief plus
that one question list, and record the gate result in .vibecoding-state.md.
```

**Golden transcript should show:** Genie Code reads the PRD, echoes the confirmed `catalog.schema`,
**reads the dropped file** (with citations), writes a first-pass `genie_brief.md`, presents **one
batched, pre-assumed question list** (not a drip of sequential questions), updates
`.vibecoding-state.md`, and stops — no measures invented beyond what the PRD/files/answers give.

---

### Step 2 — Profile Schema  *(deck Ex1 · "Profile Your Schema", slide 11a)*

**Leans on:** native schema tools (`readTable` / `tableSearch`) + `databricks-data-discovery`.
**Navigation:** read-only — runs from any workspace surface (no navigation needed).
**Gate:** ERD produced; schema-supportability of each candidate measure noted in the brief; result
recorded to `.vibecoding-state.md`.

```
Read docs/design_prd.md, docs/genie_brief.md and .vibecoding-state.md first.

@<source_catalog>.<source_schema> holds the tables behind our <function> reporting.

Review this schema and report back on:
- What each table contains and its grain
- How the tables join, and any primary or foreign key candidates
- Which columns carry business meaning that is not obvious from the column name
- Which of the candidate measures in the brief the schema can support today

Produce an ERD. Do not create anything yet. Report your findings so I can review them, note any
measure the schema cannot support yet, and record the gate result (ERD produced + per-measure
supportability) in .vibecoding-state.md.
```

**Golden transcript should show:** per-table grain, join/PK-FK candidates, "surprising column"
callouts, an ERD, and an explicit can/can't-support verdict per candidate measure — no assets
created.

> **`run-a` open decision (§4 spec):** in the live run, profiling happened inline during Steps 1 & 3
> and this standalone ERD beat didn't fire. Keep Step 2 explicit (an ERD artifact is good teaching
> and good evidence) *or* fold "produce an ERD" into Step 1. Left explicit here pending the call.

---

### Step 3 — Measures Analysis  *(Type B → C · `bypass_llm=true`; the gate — deck Ex1 · "Build Your Measure Inventory")*

**Reasoning split:** static template; **Genie Code** fills the table from the real Step 2 profile +
**dropped glossary** and **discovers any conflicts itself** — the template names *no* specific
measure or conflict.
**Leans on:** Genie Code reasoning on the Step 2 profile + dropped files. **Gate:** reviewed measures
table in `genie_brief.md`; ≤5 measures each with definition + source-of-truth + grain + owner;
conflicts written; **user signs off before ANY Metric View YAML.**

**Template (copy verbatim; frames the inventory, asserts no findings):**

```
Read docs/design_prd.md, docs/genie_brief.md (the Step 2 profile + candidates), any files I dropped
in, and .vibecoding-state.md first — the measures that matter follow the PRD's User Journeys.

Draft my measure inventory as a table with exactly these columns:
  Measure | Current definition (one sentence) | Source of truth (table.column or file) | Grain | Owner (a named person) | Conflict

Rules:
- Stop at five measures. Depth beats coverage — two well-governed measures beat fifteen half-
  governed ones.
- Name the source of truth as the actual table/column (or the dropped file it came from).
- Inspect the real definitions and the data: wherever the same measure could be computed or
  interpreted more than one way (e.g. different filters, grains, or gross-vs-net style choices),
  write BOTH readings in the Conflict column. The conflict is a finding you surface, not something
  I will tell you — flag it even if I didn't mention it.
- Mark any measure with no named owner as "unowned". No owner, no Metric View.

Pre-fill every cell you can from the brief and my dropped files; leave a clear "?" where you need me.
Then STOP, show me the table, and record the gate result in .vibecoding-state.md. Do NOT write any
Metric View YAML until I sign off on it.
```

**Golden transcript should show:** a filled inventory table, **at least one conflict Genie Code
surfaced on its own** (nothing about the conflict was in any prompt), unowned rows flagged, a
`.vibecoding-state.md` gate update, and an explicit "waiting for your sign-off before authoring"
stop. **This is the gate the whole revision hinges on — no YAML appears in this transcript, and no
domain finding was injected.**

> **Where the conflict surfaces:** it counts whether Genie Code raised it **at Step 1 (during
> elicitation) OR here at Step 3**. In practice a probing agent often flags the definitional clash
> while seeding the brief (Step 1); when it does, **Step 3 formalizes/confirms it in the table**
> rather than surfacing it first. Either is a pass — the check is that the conflict was
> *self-discovered*, not injected, and that it is recorded in the signed-off inventory. (Observed in
> `run-a`: the gross-vs-net / returns clash surfaced at Step 1.)

---

## Chapter: Metric View  *(deck Exercise 2)*

### Step 4 — Draft the Metric View  *(deck Ex2 · prompt 1, slide 14a; + `/importBI` Path A)*

**Leans on:** native **`using-metric-views`** + **`writing-sql`** (per `genie-code-environment` §6c —
Metric Views are FULLY native; the workshop `semantic-layer/01-metric-views-patterns` is a
CI/validation reference only); **Path A:** Genie Code native `/importBI`.
**Navigation:** created natively via `executeCode` SQL (`CREATE OR REPLACE VIEW … WITH METRICS
LANGUAGE YAML`) — runs from any workspace surface; no special page. (Extract-back for the bundle uses
`readTable → metadata.view_query_text`.)
**Gate:** each *approved* measure → 1 Metric View live; `MEASURE()` query returns; non-additive
flagged; Metric View name + gate recorded to `.vibecoding-state.md`.

> **Path A (BYO, if you have a Tableau/PBI file) — surfaced as its own "Import BI" tab in Step 4.**
> Run `/importBI` in Genie Code and upload your `.twb`/`.twbx`/`.tds`/`.tdsx` (Tableau) or `.pbit`
> (Power BI) — ≤100 MB directly, or point at a UC volume path for larger files. **Import BI produces
> MORE than a Metric View:** it builds an **AI/BI dashboard + LOCAL (dashboard-scoped) metric views +
> discovered relationships**. Those local views are **not reusable by a Genie Agent** — you must
> **promote the one(s) covering your signed-off inventory to Unity Catalog** ("Export to Metric View"
> → `@<write_catalog>.<write_schema>`). Do **not** promote every view the import produces; keep only
> what matches the brief. (For a clean model-only import, start `/importBI` from an empty UC metric
> view.) Then continue at Step 5. Docs:
> <https://docs.databricks.com/aws/en/dashboards/manage/import-bi>.

**Path B — author from the signed-off inventory:**

```
Read docs/genie_brief.md (the signed-off measure inventory) first. Use only the measures I approved.

@<source_catalog>.<source_schema> holds the tables behind our <function> reporting.

Our business has agreed the measure definitions in the brief. Use those exact definitions — don't
re-invent them.

Work out which tables, joins, and grain each measure needs. Show me what the Metric View YAML would
look like, including the dimensions people would want to slice by.

Do not save anything yet. Explain why you chose each grain, and flag any measure that is
non-additive.
```

When the YAML matches the inventory:

```
Create this Metric View as @<write_catalog>.<write_schema>.<metric_view> (my source data in
@<source_catalog>.<source_schema> may be read-only, so build it in the writable target).

Use CREATE OR REPLACE, and first check .vibecoding-state.md and the target schema for an existing
Metric View of this name — if one exists, replace it rather than making a duplicate. Use
business-friendly display names, not column names, and run a MEASURE() query afterward to prove each
approved measure returns. Then save the Metric View name and gate result to .vibecoding-state.md.
```

> If Genie Code describes a Metric View without creating it, reply: *"Create the Metric View now, do
> not just describe it."*

> **Snowflake joins (Layer-3 correction of the Layer-2 note):** nested (snowflake) joins **do work**
> in Metric Views on live Genie Code — `run-a` built `lineitem → orders → customer → nation → region`
> (plus `lineitem → part`) and every multi-hop dimension resolved, all measures returned correct
> values. The earlier Layer-2 "gotcha" was a *hand-authored CLI syntax* failure, **not** a platform
> limit. **Recommended pattern:** a **pre-joined SQL subquery** in the `source:` block (all
> dimension/measure exprs reference `source.*` at one level) — simpler plan, easier to read, and
> `run-a` confirmed it returns **identical** numbers to the nested-join version (parity). Keep
> multi-hop nesting as a working fallback. `synonyms`/`display_name`/`format` require YAML **v1.1**.

**Golden transcript should show:** grain justified per measure, non-additive measures flagged,
YAML reviewed *before* creation, then a live Metric View; a `SELECT MEASURE(...) ... GROUP BY ALL`
returns a number.

---

### Step 5 — Review & Expand Synonyms  *(deck Ex2 · prompt 2, slide 14a)*

**Leans on:** native **`using-metric-views`** (Metric View `synonyms:` field; workshop `01` is a
CI reference only). **Navigation:** native SQL rebuild — no special page.
**Gate:** ≥3 synonyms per measure/key dimension, written to the MV YAML (`synonyms:`); gate recorded
to `.vibecoding-state.md`.

> **Layer-2 confirmed:** `synonyms` **is** a Metric View YAML feature (v1.1, ≤10 per measure/field)
> — verified live. It is *also* honored by Genie/BI for term discovery, so synonyms belong **here, on
> the Metric View** (not only on the space).
>
> **Layer-3 note (review, don't add-from-scratch):** in `run-a`, Genie Code **already added synonyms
> while creating the Metric View in Step 4**. So this step is a *review-and-expand* pass, not a
> first-time add — the prompt below is worded that way.

```
Read .vibecoding-state.md first.

Review the synonyms on the Metric View @<write_catalog>.<write_schema>.<metric_view> — you likely
added some while creating it. For every measure and each key dimension, make sure the `synonyms:`
list (YAML v1.1, up to 10 each) covers: any acronym, the informal phrasing people in <function>
actually use, and any legacy name from our old reporting.

Show me the diff of what you're adding before you save, then record the gate result in
.vibecoding-state.md.

If I imported from a BI file, also pull the original field aliases from the imported workbook and
add them as synonyms.
```

**Golden transcript should show:** an existing-synonym review plus new synonyms spanning acronym +
informal + legacy for each measure; BI field aliases folded in when Path A was used; a diff reviewed
before save.

> **Deck Ex2 has a third prompt ("Add verified queries").** Verified/example queries are **not** a
> Metric View feature — they live on the **Genie space** (`instructions.example_question_sqls`),
> confirmed by the MV syntax reference (no such field) and the space's serialized structure. So that
> beat runs **in the Agent chapter, after the space exists** — see **Step 8**.

---

## Chapter: Agent + Optimize  *(deck Exercise 3 — Genie Code path)*

> **Two surfaces, one agent (deck slide 15).** The deck builds the agent in **Workbench** (Create
> Agent + **Auto-Optimize**) and names **Genie Code the sanctioned conversational fallback**: *"If
> Workbench is unavailable, Genie Code can create and curate an agent conversationally."* This track
> runs on Genie Code. The one thing the fallback loses is the **fully-automatic GSO optimizer job**
> (Workbench-only). We recover the *optimization outcome* with the **benchmark curation loop** in
> Step 10 — the same benchmarks-with-expected-answers, run via the Conversation API and fixed with
> the 5-mode table. Surface Workbench Auto-Optimize in "how it works" as the richer, hands-off
> alternative for teams who install it.

### Step 6 — Describe the Agent  *(deck Ex3 · prompt 1, slide 17a)*

**Leans on:** native `createAsset(assetType:"genie", …)` shell + the `serialized_space` contract
in **`semantic-layer/04-genie-space-export-import-api`** (validator `_assert_sql_arrays`) and
`03-genie-space-patterns` (per `genie-code-environment` §6/§6c).
**Navigation:** Genie Space is created via the native `createAsset(assetType:"genie", …)` shell then
populated with `PATCH /api/2.0/genie/spaces/{id}` — run this from a **workspace / Genie surface**, not
a bundle-editor page (surface-scoping, §1). Never `PATCH /api/2.0/data-rooms/{id}` (it wipes the
config). **Gate:** space scaffold with description; the Metric View attached under
`data_sources.metric_views`; config reviewed before creation; space id saved to `.vibecoding-state.md`.

```
Read docs/design_prd.md, docs/genie_brief.md and .vibecoding-state.md first — the agent's users and
the topics it covers come straight from the PRD's personas and User Journeys.

Create a Genie space (Genie Agent) for <function>. This agent answers questions about <what my team
reviews> for <function>. Its users are <who will ask>, and they typically ask about <two or three
topics from the brief>.

Attach @<write_catalog>.<write_schema>.<metric_view> as the only data source — it should always use
our governed Metric View rather than querying the raw @<source_catalog>.<source_schema> tables.

Show me the space's serialized config before you create it. Then create it and save the space id to
.vibecoding-state.md.
```

**Golden transcript should show:** the Metric View placed under `data_sources.metric_views` (not as
a bare table), a plain-language scope, config reviewed before creation, then a live space id captured
to `.vibecoding-state.md`.

---

### Step 7 — Author Instructions  *(deck Ex3 · prompt 2, slide 17a)*

**Leans on:** `semantic-layer/03-genie-space-patterns` (General Instructions ≤20 lines; rules, not
prose). **Navigation:** edits the existing space (`PATCH` the `serialized_space`) — from the Genie
space surface. **Gate:** instructions lean (≤~20 lines); a preferred-source rule and an explicit scope
boundary present; no contradictions; gate recorded to `.vibecoding-state.md`.

```
Read docs/genie_brief.md and .vibecoding-state.md first.

Add general instructions to the Genie space. Keep them lean — they load on every turn, so every line
must be a rule, not description.

Turn every guardrail recorded in docs/genie_brief.md into one short, plain-English rule. Always
include these two:
- For any metric in scope, query the Metric View using MEASURE(); do not re-derive metrics from raw
  fact tables.
- Scope: <what this agent covers>. Do not answer questions about <what it does not cover>.

Show me the final instruction block and cut anything that isn't load-bearing, then record the gate
result in .vibecoding-state.md.
```

**Golden transcript should show:** short, rule-shaped instructions (not prose), a MEASURE()
preferred-source rule, a scope boundary, and the agent trimming non-load-bearing lines. *(In `run-a`
this correctly cut formula internals and data-fact percentages — the Metric View already carries
those.)*

---

### Step 8 — Add Verified Queries  *(deck Ex2 · prompt 3, applied on the space)*

**Leans on:** Genie space `instructions.example_question_sqls` (**not** the Metric View) —
`03-genie-space-patterns`. **Runs after Step 6** (the space must exist). **Navigation:** edits the
existing space — from the Genie space surface. **Gate:** 2–3 verified Q→SQL examples on the *space*;
each queries the governed Metric View via `MEASURE()`; each returns; gate recorded to
`.vibecoding-state.md`.

```
Read docs/genie_brief.md and .vibecoding-state.md first.

For my Genie space, add verified example queries (question → SQL) for the two or three questions our
<function> users ask most often — pull them from the brief.

Each SQL must query the governed Metric View @<write_catalog>.<write_schema>.<metric_view> via
MEASURE() with the correct filters. These are answers Genie will reuse instead of reasoning from
scratch, so make them exact.

Show me each question/SQL pair, run each once to prove it returns, save them to the space, then
record the gate result in .vibecoding-state.md.
```

**Golden transcript should show:** 2–3 example_question_sqls saved to the *space* (not the MV), each
`MEASURE()`-based, each executed once to prove it returns.

---

### Step 9 — Load Benchmarks (with expected answers)  *(deck Ex3 · prompt 3 + Optimize "Add Benchmarks", slides 17a/36)*

**Leans on:** `03-genie-space-patterns` Rule 12 (prompt the user for benchmarks *before* generating
synthetic ones — the app can pre-collect the user's real questions). **Navigation:** edits the
existing space — from the Genie space surface. **Gate:** 10–20 benchmarks, **every one with expected
SQL**; the space answers at least one real question correctly; gate recorded to `.vibecoding-state.md`.
**Expected answers are the user's to verify.**

```
Read docs/design_prd.md, docs/genie_brief.md and .vibecoding-state.md first — the questions to
benchmark are the PRD's User Journeys.

Based on the Metric View attached to this space, suggest 15 benchmark questions a <function> user
would ask — from simple single-measure lookups to comparisons across time and dimensions.

Add them as benchmarks, and for EACH one include the expected SQL (correct filter + MEASURE()
wrapping) as the expected answer — a benchmark with a question but no expected answer cannot be
scored, so the optimizer has nothing to work against.

Then STOP: the generated QUESTIONS are a starting point, but the generated ANSWERS are a guess. I
will verify the expected answer on each before we treat any as validated. A benchmark set validated
against itself scores well and means nothing. Record the gate result in .vibecoding-state.md.
```

**Golden transcript should show:** 10–15 benchmarks **each with expected SQL**, an explicit "verify
these answers yourself" stop, and at least one real question answered correctly by the live space.
**The expected-answer-per-benchmark requirement is what makes the Step-10 optimize loop possible** —
this is the deck's "expected answers are required" rule, and the thing `run-a` skipped.

---

### Step 10 — Optimize: Run Benchmarks → Fix → Re-run  *(deck Ex3 Optimize "Run Benchmarks" + Part 7, slide 28 — the GC-native optimize loop)*

**Leans on:** `03-genie-space-patterns` Rule 17 (**append-only** optimize — never replace validated
instructions) + the **benchmark regression template** + Conversation-API validation
(`assets/templates/genie-space-regression-test.py`). **Navigation:** the run uses the Conversation
API (`ask_genie`) from any workspace surface; the fixes edit the existing space. **Gate:** benchmarks
run via the Conversation API; each failure triaged to ONE curation fix (the 5-mode table); fixes
**appended**; re-run with an improved rate; before/after pass rate recorded to `.vibecoding-state.md`.
Accuracy target is *guidance*, **~85%** (§11 Q5) — not a hard gate.

> **Why here (before Domains/Pages):** this loop optimizes the **Genie space** against its own
> benchmarks — it depends only on the Metric View + instructions + verified queries built in Steps
> 4–9, not on Domains/Pages (which ground **Genie One**, not this space's benchmark run). So you get a
> working, scored agent *first*, then layer on the broader ontology (Steps 11–13).
>
> **This is the optimization the deck calls for, done the way Genie Code can actually invoke it.** The
> automatic **Workbench GSO job is Workbench-only**; here Genie Code runs the loop itself via
> `ask_genie`. The `run-a` weakness was stopping after "propose a fix" — this step **closes the loop**
> (apply → re-run → score).

```
Read docs/genie_brief.md and .vibecoding-state.md first.

Run all the benchmark questions against this Genie space using the Conversation API. For each one,
show: the question, the SQL Genie chose, the answer, and whether it matched the expected answer and
obeyed the brief's guardrails. Report the overall pass rate.

For every miss, diagnose the root cause and map it to ONE curation fix using this table:
  Right measure not found       → add synonyms (on the Metric View)   (most common)
  Wrong source found            → tighten scope in the instructions
  Outdated pattern used         → mark the asset deprecated
  Critical filter missed        → add it to the instructions
  Tables joined wrongly         → add a join hint or a verified query

Show me the fixes before applying them. APPEND new rules to the existing instruction block — never
replace it (existing rules were already validated). Then re-run the benchmarks and show me the
before/after pass rates. Aim for ~85% on the questions I verified — don't chase 100%. Record the
before/after pass rate in .vibecoding-state.md.
```

**Golden transcript should show:** a baseline pass rate, a failure→fix mapping per failure (each fix
from the 5-mode table), **applied append-only fixes**, and a **re-run** with an improved rate — the
fixes being *curation* (synonyms, scope, instructions, verified queries), not model changes.

> **Domain scoping is an *additional* retrieval lever that lands in Ex4 (Steps 11–13).** Once a domain
> exists, "wrong source found" can also be fixed by scoping with a domain / a routing Page; you may
> re-run this loop after Ex4 to capture that gain. In v1 the first optimize pass uses instruction
> scoping only, since the domain isn't built yet.

---

## Chapter: Domain & Pages  *(deck Exercise 4 — CORE; created in the Discover UI)*

> **Beta caveats (state them in the app's "how it works"):** Pages is **Beta**; it has **no public
> create/update API** — Pages are authored in the **Discover UI** with Genie Code assisting inside
> the Page editor (expect to paste a draft rather than have it created headlessly). Pages currently
> ground **Genie One** answers (shown as citations); integration with Genie Agents / Genie Code is on
> the roadmap. You need **Manage Discovery** permission on the domain. *(Skill:
> `data_product_accelerator/skills/semantic-layer/06-genie-discover-ontology` — the reference +
> drafting contract for Steps 11–13.)*

### Step 11 — Model the Domain + Subdomains  *(deck Ex4 · prompt 1, slide 22a)*

**Preferred method — create it in the Discover UI (not Genie Code).** Domains and subdomains are a
few clicks in the UI and easiest to see there: navigate to **Catalog → Discover → New domain**, add
3–5 subdomains, and note the domain + subdomain IDs. Needs **Manage Discovery** permission.

> **If the workshop pre-creates a domain, use it** — skip creation entirely; just open it in Discover
> and capture its domain + subdomain IDs. The app can pre-fill `{domain}` with the workshop domain so
> everyone shares one clean taxonomy.

**Navigation:** Discover UI (Catalog → Discover). **Gate:** a domain with 3–5 subdomains exists (new
or pre-created); its domain + subdomain IDs captured to `.vibecoding-state.md` for later steps.

*Optional Genie Code assist (fallback only — prefer the UI above):*

```
Read docs/design_prd.md and .vibecoding-state.md first — the domain scope follows the PRD.

If a domain called <domain> already exists, use it — just show me its domain and subdomain IDs.
Otherwise create a domain called <domain> with these subdomains: <subdomain_1>, <subdomain_2>,
<subdomain_3>, covering <one sentence describing scope> for <function>.

Either way, show me the domain and subdomain IDs and save them to .vibecoding-state.md.
```

**Golden transcript / result should show:** a domain + 3–5 subdomains present (created in the UI or
reused from the workshop), IDs saved to state, no Pages authored yet.

---

### Step 12 — Author Pages  *(deck Ex4 · prompt 2 + bulk-import prompt 3, slide 22a)*

**Navigation:** authored in the **Discover UI Page editor** (no public create/update API) — navigate
to Discover → your `<domain>` → the `<subdomain>` → **New Page**; Genie Code drafts the fields inside
the editor (expect to paste the draft). **Gate:** two published Pages, each with a full synonym list
and at least one negative rule; every rule sentence is chunk-safe (names its table/measure inside the
sentence); published Page IDs recorded to `.vibecoding-state.md`.

```
Read docs/genie_brief.md and .vibecoding-state.md first.

Create a Page in the <subdomain_1> subdomain of <domain> for the measure "<measure>".

Use docs/genie_brief.md (and any file I dropped in) as the source. The Page needs:
- A definition in plain business language, one paragraph
- The exact formula, naming @<write_catalog>.<write_schema>.<metric_view> and the measure
- Synonyms covering every way someone might ask — acronym, informal phrasing, legacy name
- At least one negative rule (a "never do this")
- The governed Metric View as a related asset

Write every rule sentence so it names the table or measure inside the sentence itself — the Page is
split into chunks before it is read, so a sentence that leans on the title arrives orphaned. Show me
the draft before publishing. Then repeat for my second most important measure, and save the published
Page IDs to .vibecoding-state.md.
```

**Bulk import (optional — if you have a glossary):**

```
I have an existing glossary at <byo_glossary_file>. Import these as Pages into the domain with ID
<domain_id from Step 11>. Map each term to a Page with a definition, synonyms, and related assets.

Show me the first three before creating all of them.
```

**Golden transcript should show:** two published Pages, each with a definition (business language),
the exact formula naming the Metric View, a synonym list spanning acronym/informal/legacy, and ≥1
negative rule; chunk-safe sentences; drafts reviewed before publish. *(Bulk-import failures usually
mean the domain **name** was passed where the internal **ID** is needed, or missing Manage Discovery.)*

---

## Chapter: Routing Page  *(deck Exercise 5 — CORE)*

### Step 13 — Write the Routing Page  *(deck Ex5 · prompt, slide 26a)*

**Navigation:** authored in the **Discover UI Page editor** (no public API) — navigate to Discover →
your `<domain>` → **New Page**. **Gate:** one Routing Page covering every measure in the signed-off
inventory, published, with a named owner; Page ID + owner recorded to `.vibecoding-state.md`.

```
Read docs/genie_brief.md and .vibecoding-state.md first (use the domain ID saved in state).

Create a Page in <domain> called "Question to Metric View Routing".

Its purpose is to map the ways people ask questions to the governed Metric View and measure that
should answer them. For each measure in my signed-off inventory (docs/genie_brief.md), list four or
five phrasings — the formal name, the acronym, the informal phrasing, and any legacy name from an old
system — and route each to @<write_catalog>.<write_schema>.<metric_view> and the exact measure.

Format the mappings as a table. Add a short introduction saying this Page routes questions to
governed sources and should be checked before querying raw tables. Link the Metric View as a related
asset, name an owner, show me the draft before publishing, then record the Page ID + owner in
.vibecoding-state.md.
```

**Golden transcript should show:** a flat phrasing→(Metric View, measure) table covering every
inventory measure — including the acronyms and sloppy phrasings — a named owner, and a draft reviewed
before publish. *(This is the deck's highest-return exercise: it replaces Genie's table-inference
with a lookup a person already got right.)*

---

## Chapter: Close  *(deck Part 7 curation checklist, slide 29)*

> The optimize loop that reads the score and applies fixes is **Step 10** (end of the Agent chapter,
> before Domains/Pages). This close is the deck's "what done looks like" summary — run it after
> Ex4/Ex5 so the per-metric Page rows apply.

**Curation checklist (deck slide 29 — record the result in `.vibecoding-state.md`):**
- *Per metric:* a Page with the formula, full synonyms, domain/subdomain, ≥1 negative rule, pointer
  to the governed source.
- *Per agent:* scope (in/out), preferred source, 3–5 SQL examples, known caveats.
- *Per Metric View:* business-readable names, contextual dimensions, descriptions, non-additive flagged.
- *Before you leave:* pick two metrics and a date to curate next — write them down.

---

## Chapter: Share  *(deck Exercise 6)*

### Step 14 — Show Your Agent

No new asset — this is the proof beat. **Navigation:** open the Genie space chat surface. Ask the
agent **one real question you actually needed answered this quarter** (not one you know it can handle)
and confirm it: uses `MEASURE()` on the governed Metric View, discloses the time anchor when a
relative expression is used, and respects the scope boundary. Note what it got right and the one thing
you'd curate next (feeds the next benchmark round) — record that note in `.vibecoding-state.md`.

**Golden transcript should show:** a live, real question answered correctly through the Metric View,
with the time-anchor disclosure and scope behavior visible.

---

## Chapter: Activation tail  *(optional — beyond the deck; design spec §9)*

These steps are **soft-recommended, not part of the core happy path**. Each is a single review-then-
build beat on the writable target.

### Step 15 — Dashboard  *(AI/BI on the Metric View)*

**Leans on:** AI/BI native — authored **by navigation** (`genie-code-environment` §6c).
**Navigation (load-bearing):** Genie Code creates the shell with `createAsset(assetType:"dashboard")`
then **auto-navigates** `openAsset(assetType:"dashboard", …)` to the **dashboard canvas** — **widget
editing requires being on the canvas page; there is no remote widget edit.** If tile authoring stalls,
it is almost always a wrong-surface signal — open the dashboard (Genie Code prints the clickable link)
and continue there. **Gate:** dashboard live; tiles query the Metric View (via `MEASURE()`), not raw
tables; dashboard id recorded to `.vibecoding-state.md`.

```
Read docs/genie_brief.md and .vibecoding-state.md first.

Create an AI/BI dashboard for <function> built on @<write_catalog>.<write_schema>.<metric_view>. Add
tiles for each governed measure (using MEASURE()) sliced by the key dimensions in the brief. Show me
the tile plan before building. Then create the dashboard, open it on the canvas so the widgets can be
authored there, give me the link, and save the dashboard id to .vibecoding-state.md.
```

### Step 16 — Synced Tables → Lakebase → App  *(optional operational surface)*

**Leans on:** `databricks-lakebase`, `apps_lakebase` skills. Spin up Lakebase, sync the governed
gold/Metric-View outputs, and stand up an AppKit app to visualize them. Follow the AppKit scaffold →
wire → deploy skills; keep the app under its own `<app_name>/` root (see AGENTS.md artifact rules).
**Navigation:** `apps init` needs `--output-dir` (it ignores the page CWD); the reliable deploy is the
**SDK SNAPSHOT path** (`w.apps.deploy(…, mode=SNAPSHOT)`), not `apps deploy` via CLI — see
`genie-code-environment` §4. Record the app URL + Lakebase project to `.vibecoding-state.md`.

### Step 17 — Productionize as a DAB  *(optional)*

**Leans on:** `databricks-asset-bundles`. Package the Metric View, Genie space export, and dashboard
as a Databricks Asset Bundle so the whole track redeploys reproducibly. Keep dev files vs. the prod
bundle boundary explicit (design spec §9). **Navigation (load-bearing):** `bundle deploy` is pinned to
the **bundle-editor page** of the bundle root — write `databricks.yml` under the bundle root, **open
that folder's bundle editor**, then run `bundle validate`/`deploy --target dev` there. A "blocked" /
`databricks.yml not found` message means you are on the wrong page — open the bundle editor; never fall
back to raw SQL or the Jobs/Pipelines REST API (`genie-code-environment` §3). Record the bundle deploy
target + result to `.vibecoding-state.md`.

---

## Validation runbook (the Phase-1 spike)

Per the design spec §10 Phase 1: run these prompts **by hand on live Genie Code** against **two
reference schemas**, exercise BYO context **both ways** (drop a file into Genie Code + `/importBI`),
prove the **Measures-Analysis gate** and the **Step-10 optimize loop**, restore **Ex4/Ex5**, and save
the resulting **Genie Code transcripts as golden references** under `phase1-evidence/`. Open every run
with the `vibecoding-state` bootstrap/`enter` and close it with `exit`; capture the
`.vibecoding-state.md` delta after each step. For **Step 0 (the only Type A step)**, also save the
**app-generated PRD prompt** as a separate artifact.

**Matrix:**

| Run | Schema | Exercises | Must prove |
|---|---|---|---|
| A | **Clean-Gold** (a well-modeled `catalog.schema`) | `vibecoding-state` enter → Step 0 (PRD) → Steps 1–14, Path B; BYO via file-add (**drop `{byo_glossary_file}` into Genie Code** at Step 1) → exit | Full happy path end-to-end; brief seeded from the dropped file; gates hold; optimize loop closes; Ex4/Ex5 published; state persists across steps |
| B | **Raw / needs-synthetic** (no usable data) | Step 1 synthetic toggle → Faker, then Steps 2–14; BYO via `/importBI` (a `.twbx`/`.pbit` at Step 4 Path A) | Adaptive synthetic branch; `/importBI` → Metric View; gates hold; optimize loop closes |

**Gate-specific checks (both runs):**
- **Measures-Analysis gate:** Step 3 transcript contains the reviewed table and **no** Metric View
  YAML; Step 4 only proceeds after an explicit sign-off line.
- **Unprompted conflict discovery (realism):** no prompt names a conflict, yet the transcripts show
  Genie Code surfacing at least one on its own from the profile + dropped file — **at Step 1
  (elicitation) OR Step 3 (inventory)**. If it surfaced at Step 1, Step 3 must still *record* it in
  the signed-off table. *This is the headline realism check* — if the conflict only appears because
  we told it, the test is invalid.
- **Optimize loop closes (Step 10):** every benchmark has an expected answer; the loop runs via the
  Conversation API, maps each miss to a 5-mode fix, **appends** (not replaces) instruction changes,
  and **re-runs** with a reported before/after pass rate. A transcript that stops at "here's a
  proposed fix" (as `run-a` did) is a **fail** for this check.
- **Ex4/Ex5 published:** a domain with subdomains exists; two measure Pages and one Routing Page are
  published, each with a synonym list and (for measure Pages) ≥1 negative rule; the Routing Page has
  a named owner.
- **PRD spine:** Step 1 transcript shows the agent quoting `design_prd.md` User Journeys / Data
  Entities rather than re-asking them.
- **Type A capture (PRD only):** the app-generated PRD prompt is saved *separately* from the Genie
  Code transcript; Steps 1–14 use the verbatim static templates (no per-step app generation).
- **State persistence:** `.vibecoding-state.md` shows each step's gate result accumulating across
  the run (not reset per prompt).
- **BYO file-add:** Genie Code reads the **dropped** `{byo_glossary_file}` and at least one measure
  definition in the brief is traceable to it.
- **BYO `/importBI`:** a Metric View originates from the `/importBI` payload, with its field aliases
  surviving as synonyms in Step 5.

**Acceptance:** each step reliably (a) triggers the interview, (b) produces its artifact, (c) passes
its gate, (d) a conflict is discovered unprompted (at Step 1 or Step 3) and recorded in the signed-off
inventory, and (e) the Step-10 optimize loop closes to a re-run pass rate — text iterated until true,
transcripts + state deltas saved under `phase1-evidence/` for Phase 2 to encode against.

---

## Layer-2 validation results (live `samples.tpch` on `fevm-serverless`, 2026-09-13)

Proxy validation via CLI (`--profile fevm-serverless`); assets created in
`serverless_stable_6t92c3_catalog.genie_accel_phase1`:

- **Steps 1–3 (read-only):** schemas confirmed; gross `SUM(l_extendedprice)` = **1.147T** vs net
  `SUM(l_extendedprice*(1-l_discount))` = **1.090T** (~5% — the real Finance-vs-Sales-Ops conflict);
  AOV non-additive; on-time rate computable from `l_receiptdate` / `l_commitdate`. ✔
- **Step 4 (Metric View):** `order_revenue_metrics` created (single-level `orders` join); a
  `MEASURE()` query returned monthly gross / net / units / AOV / on-time. ✔
- **Step 4 gotcha (later corrected in Layer 3):** hand-authored nested-join CLI syntax failed; the
  platform is fine — see the Layer-3 correction and the Step 4 note.
- **Step 5 (synonyms):** ✔ MV re-created with `synonyms:` on every measure/dimension — **confirmed a
  Metric View v1.1 feature** (also honored by Genie/BI).
- **Verified queries:** ✖ **not** a Metric View feature → Genie space
  `instructions.example_question_sqls` (now Step 8, after the space exists).
- **Space / benchmarks:** `databricks genie create-space` exists but requires a full
  `serialized_space` (the easy `table_identifiers` path is MCP-only); benchmarks have
  `databricks genie genie-create-eval-run` (Beta). Live space build deferred to **Layer 3** (real
  Genie Code) where the native `genie_space` skill authors the serialized contract.

---

## Layer-3 validation results (live Genie Code, `run-a`, 2026-09-13)

Real Genie Code in-workspace (`client_context=genie_code`), source `samples.tpch` (read-only), assets
written to `serverless_stable_6t92c3_catalog.revenuescope`. Full transcript in `phase1-evidence/run-a/`.

- **Session/PRD (Step 0):** `vibecoding-state` resolved `artifact_root` to the git-cloned user project
  (not the `.assistant/skills` copy, not the page CWD); PRD written to `docs/design_prd.md`. ✔
- **Locate/brief (Step 1):** brief seeded from PRD + schema; **conflict discovered *during
  elicitation*** (gross-vs-net / returns) — unprompted. ⭐ *Finding:* one-question-at-a-time dripped
  3 sequential Qs → **Step 1 prompt changed to batch all questions with pre-filled assumptions.**
- **Measures gate (Step 3):** honored **stop-at-five**; surfaced **three data-grounded conflicts
  unprompted** — tax-basis additivity (`o_totalprice` tax-incl vs net tax-excl, ~4%), return-rate
  denominator (24.69% line-item vs 43.07% order-level), and the `COUNT(*)` vs `COUNT(DISTINCT)` grain
  trap. No YAML until sign-off. ✔ **Headline realism check passed.**
- **Metric View (Step 4):** built + validated. **Nested snowflake joins WORKED** (4-level
  `lineitem→orders→customer→nation→region` + `part`); a pre-joined-subquery rebuild returned
  **identical** numbers (parity) → **Layer-2 "gotcha" corrected** (see Step 4 note). Validated
  aggregates: Net **1,089,835,179,247**, Gross **1,147,191,013,439** (Gross = Net + Discount holds),
  AOV **145,311** (net-based, not tax-incl 151,125), Order Count **7,500,000** (`DISTINCT`), Return
  Rate **24.69%** (line-item). ✔
- **Synonyms (Step 5):** already added during Step 4 → **reframed as review/expand** (see Step 5). ✔
- **Agent build (Steps 6–9):** space created on the **governed Metric View only** (verified via
  `askGenieSpace` — 11 dims + 5 measures visible); instructions authored lean (correctly cut formulas
  + data-fact %); 3 verified queries saved to the **space**; 15 benchmarks drafted with expected SQL. ✔
- **⚠️ Degradations (fixed in this r7 rewrite):** the agent was built on the GC path with **no closed
  optimize loop** — the run stopped at "propose a fix," never re-ran, never scored; **Ex4/Ex5
  (Domains, Pages, Routing) were skipped entirely.** Step 10 now closes the loop (append-only fixes →
  re-run → ~85%), placed **before** Domains/Pages, and Ex4/Ex5 are restored as core chapters. See
  `phase1-evidence/run-a/step-05-to-10-agent.md`.
- **Source vs write target:** `samples.tpch` read-only forced a separate writable schema; Genie Code
  had to *guess* one → **added `{write_catalog}.{write_schema}` variable** (Conventions + Steps 4/6/13/15).
- **Step 2 (Profile) absorbed:** profiling happened inline during Steps 1 & 3; the standalone ERD beat
  didn't run. *Open decision:* keep Step 2 explicit or fold "produce an ERD" into Step 1 (see spec §4).

---

## What I (the assistant) can do vs. what needs a human

I cannot *be* Genie Code (it is the in-workspace agent). Two ways to run the spike:

1. **You drive Genie Code** with the prompts above and paste back / save the transcripts. This
   produces the true golden references.
2. **I run a proxy validation via the Databricks MCP tools** (`get_table_stats_and_schema`,
   `execute_sql`, `manage_metric_views`, `manage_genie`, `ask_genie`) to prove the *operations* each
   prompt triggers are feasible on your live schema. This is not a Genie Code transcript, but it
   de-risks feasibility fast. **Read-only** for Steps 1–3 (profiling, ERD inputs, measure
   supportability); **asset-creating** for Steps 4–15 (Metric View, Genie space, benchmarks,
   dashboard) — so it needs your go-ahead on a target location. Ex4/Ex5 (Pages) have **no public API**
   so they can only be validated in the Discover UI (Layer 3).

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

**Answer key — what a correct run *should* surface (⚠️ do NOT paste this into Genie Code):**

This table is the **grader's key**, not a prompt. The whole point of the realism pass is that Genie
Code discovers these from the profile + dropped file *without being told*. Use it only to check the
Step 3 transcript.

| Measure | Expected definition | Source of truth | Grain | Conflict Genie Code should find on its own |
|---|---|---|---|---|
| Revenue | Net of line discount: `SUM(l_extendedprice * (1 - l_discount))` | `lineitem` | line | Gross `SUM(l_extendedprice)` (no discount) also circulates — two numbers, same name. Genie Code should spot both from the discount column + any glossary and write both. |
| Average Order Value | Net revenue ÷ distinct orders — non-additive (never average across periods) | `lineitem` + `orders` | order | Should be flagged non-additive. |
| Units Sold | `SUM(l_quantity)` | `lineitem` | line | — |

The **Revenue gross-vs-net** row is the *unprompted conflict* the Step 3 transcript must surface (not
silently pick one); **Average Order Value** is what Step 4 must flag as non-additive and Steps 7/8
must protect with `MEASURE()`. **If the transcript only shows these because the prompt named them,
the run fails the realism check.**

**Filled Step 2 (Profile) — paste into Genie Code (tag `@samples.tpch` first):**

```
Read docs/genie_brief.md and .vibecoding-state.md first.

@samples.tpch holds the tables behind our order & revenue reporting.

Review this schema and report back on:
- What each table contains and its grain (lineitem vs orders especially)
- How the tables join, and any primary/foreign key candidates
- Which columns carry business meaning not obvious from the name (e.g. l_returnflag, o_orderstatus)
- Which measures for order & revenue reporting the schema can support today

Produce an ERD. Do not create anything yet. Report your findings so I can review them.
```

**Filled Step 3 (Measures Analysis gate) — paste next.** This is the **generic Step 3 template
verbatim** (no measures, no conflict injected): use it exactly as written in Step 3 above. Do **not**
seed it with Revenue / gross-vs-net — let Genie Code derive the inventory and the conflict from the
Step 2 profile + your dropped glossary, then check the result against the answer key.

**Then** Step 4 Path B drafts the Metric View for the two signed-off measures (whatever Genie Code
and you converged on — expected: net Revenue + Average Order Value), with the non-additive measure
flagged — exactly the deck's "why `MEASURE()` isn't optional" demonstration, on real numbers.

For the **Ex4/Ex5 chapters** on this example: domain = `Revenue Analytics`, subdomains e.g.
`Orders`, `Returns`, `Customers`; author measure Pages for *Net Revenue* and *Return Rate* (each with
a negative rule — e.g. "never average AOV across periods"); the Routing Page maps "revenue / net
sales / top line", "AOV / revenue per order", "return rate / returns %" to the Metric View measures.

**Run B (raw/synthetic):** at Step 1 choose the synthetic toggle → Faker generates a small
`<catalog>.<schema>` for `<function>`; the remaining steps are identical. Exercise BYO via
`/importBI` here by running it on a Tableau/PBI file at Step 4 Path A.
