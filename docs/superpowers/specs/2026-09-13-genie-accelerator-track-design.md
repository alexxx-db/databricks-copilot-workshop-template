# Genie Accelerator Track — Design Spec

**Status:** Design-complete (Phase 0). Ready to drive Phase 1 (prompt drafting + live validation).
**Date:** 2026-09-13
**Scope:** Revamp of the app's `genie-accelerator` workshop track, optimized for Genie Code as the execution surface.

**Revision (2026-09-13, r2) — folds in five review revisions:**
1. **Deck-aligned granularity.** The core is re-expanded from 5 condensed steps back to the deck's
   right-sized chunks (Metric View draft / synonyms / verified queries as separate beats; agent
   describe / instructions / benchmarks as separate beats). We keep the *chunking* and add
   interactivity + context — we do not re-condense.
2. **`design_prd.md` is the spine's head.** `docs/genie_brief.md` now **extends** the
   `prd_generation`-authored `docs/design_prd.md` (reads its *User Journeys* + *High-Level Data
   Entities*) instead of starting cold.
3. **Structured schema input.** The entry reuses the app's existing `LakehouseParams` /
   `chapter_3_lakehouse_catalog` / `chapter_3_lakehouse_schema` machinery so prompts arrive at Genie
   Code carrying the real `catalog.schema` (not a `<placeholder>`); a "no data → synthetic" toggle
   routes to the Faker path.
4. **Bring-your-own context.** Two ingestion lanes seed business definitions: (a) app-side
   attachments (Excel / PDF / dashboard screenshots) via the existing FM-API attachment flow, and
   (b) Genie Code's native `/importBI` for Tableau / Power BI files → Metric Views.
5. **Explicit Measures Analysis gate** *before* any Metric View YAML, plus a
   `verify_genie_track_flow.py` CUJ verifier mirroring `scripts/verify_agent_track_flow.py`.

**Revision (2026-09-13, r3) — reasoning-surface allocation:**
- Two reasoning surfaces are now allocated **by pedagogy** (new **§5.1**): the **app** FM API
  generates a personalized, ready-to-paste prompt (the `prd_generation` *meta-prompt* pattern) for
  the intent/discovery beats; **Genie Code** does the *content* reasoning on real UC schema + files
  the user drops in. Every step is tagged **Type A** (app-generated), **B** (template + variable
  substitution), or **C** (data-grounded — Genie Code reads dropped files).
- **BYO context is primarily Genie Code file ingestion** (drop Excel/CSV/docs/BI exports into the
  repo; it reasons on the real content). The app's FM-API attachment path is demoted to the
  *secondary, intent-stage* lane. `/importBI` remains the Tableau/PBI special case.

**Revision (2026-09-13, r4) — Layer-2 live-validation corrections (on `samples.tpch`):**
- **Synonyms are a Metric View feature** (YAML v1.1 `synonyms:`, ≤10 per measure/field) — verified
  live by re-creating the MV with synonyms on every measure/dimension. Step 5 stays in the
  Semantic / Metric-View chapter (synonyms are *also* honored by Genie/BI for discovery).
- **Verified / example queries are NOT a Metric View feature** — they are a Genie-space feature
  (`instructions.example_question_sqls`). **Step 6 moves from the Semantic chapter to the Agent
  chapter**, and runs *after* the space exists (Step 7).
- **Snowflake gotcha:** nested (snowflake) join dimension referencing is finicky; prefer
  single-level joins or a pre-joined source view for multi-hop dimensions (Region / Market Segment).
- **Genie space creation modality:** `databricks genie create-space` requires a full
  `serialized_space` (the easy `table_identifiers` path is MCP-only), so the space build stays a
  Genie-Code / MCP beat (Layer 3), not raw CLI.

**Revision (2026-09-13, r5) — realism pass (shrink Type A; discover, don't inject):**
- **One Type A step.** The **PRD** is now the *only* app-generated prompt. Steps 1 (Locate) and 3
  (Measures Analysis) are re-tagged **static templates** (Type C / B) — Genie Code reasons on the
  real schema + dropped files. The app can't see measures/conflicts, so personalizing them app-side
  would mean *inventing* them; static templates are also exactly what Phase 2 encodes. (§5.1 table
  + prose, Principle 9, Q10 updated.)
- **PRD points at the real source.** The PRD beat references the shipped
  `apps_lakebase/prompts/sections/03-prd_generation.md` (`## System Prompt`), not a hand-written
  mimic. Faithful Type A output comes from that file through the FM API (or the app), not the spec.
- **Conflicts are discovered, not injected.** No prompt asserts a domain conflict (e.g. gross vs.
  net revenue). Genie Code must surface it from profiling + the dropped glossary. "Unprompted
  conflict discovery" is now a **Phase-1 acceptance check** (§10 harness); the `samples.tpch`
  gross/net numbers move to an *answer key* the runner checks against, never a prompt input.
- **`vibecoding-state` wired into the runbook.** Each run opens with the state bootstrap/`enter`
  (resolve `artifact_root`, load client context) and closes with `exit`; `.vibecoding-state.md`
  deltas are captured per step as evidence.
- **BYO file parameterized** as `{byo_glossary_file}` (the user's own export) — no fictional
  `revenue_definitions.xlsx`.

**Revision (2026-09-13, r6) — Layer-3 live-Genie-Code run (`run-a`, evidence in `phase1-evidence/`):**
- **Headline check passed.** On live Genie Code, the Measures gate surfaced **three data-grounded
  conflicts unprompted** (tax-basis additivity, return-rate denominator, `COUNT(*)` grain trap) and
  held **stop-at-five** — proving "discover, don't inject" end-to-end. The gross-vs-net conflict
  actually surfaced at **Step 1 (elicitation)**; Step 3 formalized it (see the Step-1-or-3 wording).
- **Nested snowflake joins work — Layer-2 "gotcha" corrected.** Genie Code built a 4-level
  `lineitem→orders→customer→nation→region` Metric View with all dimensions resolving; a pre-joined
  source subquery returned identical numbers. The pre-joined pattern is now *recommended*, not
  *required*. (§6 Metric-View row + prompts Step 4 updated.)
- **Source vs write target split.** `samples.tpch` was read-only, so governed assets needed a
  separate writable schema — `{write_catalog}.{write_schema}` distinct from the Step-1 `{source_*}`,
  never guessed by Genie Code. **No new variables/pair are needed (corrected 2026-09-13):** source maps
  to the app's existing `{chapter_3_lakehouse_catalog}` / `{chapter_3_lakehouse_schema}`
  (`LakehouseParamsEditor`), write maps to `{lakehouse_default_catalog}` + the `GoldTableTargetEditor`
  schema/prefix (there is no `lakehouse_default_schema` param). Metric-view name → Genie Code suggests;
  domain/subdomains → UI-first; BYO glossary/BI → uploaded. See the Phase-2 plan §1 mapping table.
- **Batch the interview.** One-question-at-a-time dripped 3 sequential questions; Step 1 (and the §5
  shape) now ask for **all** questions in one batched list with pre-filled assumptions.
- **Synonyms are added during Step 4** in practice → Step 5 reframed as *review & expand*.
- **Step 2 (Profile) was absorbed** into Steps 1 & 3 (no standalone ERD run). *Open decision (§4):*
  keep Step 2 explicit or fold "produce an ERD" into Step 1.
- **Prompt calibration reaffirmed.** Prompts stay at the **"Genie in a Bottle" deck** richness
  (conversational ~8–15 line blocks with a "review before you build" close), not one-line commands.

**Revision (2026-09-13, r7) — FINALIZED alignment: the deck is the spine, enhancements only:**
Honest assessment after the full `run-a` pass: the **Discover → Metric View** half (deck Ex1–Ex2) is
strong, but the **Agent → Validate** half degraded and **Ex4–Ex5 went missing**. Root cause: we
replaced deck mechanisms with weaker improvisations. This revision re-anchors every step to the
deck's canonical prompts and admits **only** the enhancement whitelist below.

- **Canonical spine = the six deck exercises, in order, using the deck's prompt text where it exists:**
  - **Ex1 Discover** (Genie Code): Measure Inventory + *Profile Your Schema* (deck 11a).
  - **Ex2 Metric View** (Genie Code): Draft → Synonyms → Verified Queries → promote (deck 14a #1–3).
  - **Ex3 Agent + Auto-Optimize** (**Workbench primary**, Genie Code documented *fallback*):
    Describe → Instructions → 10–20 Benchmarks w/ **expected answers** → **Launch Auto-Optimize**
    (deck 17a). *This reverses our Genie-Code-only, no-optimizer path.*
  - **Ex4 Domain & Pages** (Genie Code assists in the Discover UI): domain + subdomains → author
    Pages → bulk import (deck 22a #1–3). Beta / no public API / grounds Genie One — caveated, not dropped.
  - **Ex5 Routing Page** (deck 26a): phrasing → Metric View + measure.
  - **Part 7 Validate:** read accuracy (baseline vs optimized) → map failures to the **5-mode fix
    table** (right Page not found→synonyms; wrong Page→domain scope; outdated→deprecate; filter
    missed→instructions; bad join→join hint) → accept/reject optimizer edits → re-run, target **≥85%**.
  - **Ex6 Share** + our optional **Activation tail** (dashboard → synced tables → Lakebase → App → DAB).
- **Enhancement whitelist (the ONLY sanctioned deviations, each justified):**
  1. **Step 0 PRD (Type A)** + **`vibecoding-state`** spine — persistence/context the deck lacks.
  2. **Structured source+write input** (`LakehouseParams` ×2: `{source_*}` and `{write_*}`).
  3. **BYO context** = Genie Code file-add + `/importBI` (both deck-sanctioned).
  4. **Discover-don't-inject** measures gate (matches deck Ex1 spirit; proven unprompted in `run-a`).
  5. **Batch the interview** (one numbered list, pre-filled assumptions).
  6. **MV corrections:** nested joins work / pre-joined recommended; idempotent `CREATE OR REPLACE`.
  7. **Verified queries attach to the space** (deck 14a #3 wording is loose — MVs have no
     `example_question_sqls`; keep the *draft* in Ex2, *apply* on the space in Ex3).
  8. **Optional Activation tail** (dashboard / Lakebase / App / DAB) — beyond the deck, clearly optional.
- **Deviations to REVERSE (degradations):** (a) Genie-Code-primary agent with no optimizer →
  Workbench Auto-Optimize primary; (b) manual "run each benchmark" → the optimize→failures→fix→re-run
  loop; (c) Ex4–Ex5 dropped → restored with Beta caveats; (d) drift/over-scaffolding → snap to deck text.
- **Two scope decisions RESOLVED (operator, 2026-09-13):**
  1. **Agent/optimizer surface = Genie-Code-first, workshop-style optimize loop.** Ex3 stays on Genie
     Code (our execution surface) but MUST call for optimization the workshop way. **Mechanism
     verified against the `genie-space-patterns` skill:** the fully-automatic **Workbench GSO
     "Auto-Optimize" job is Workbench-only — Genie Code cannot launch it**; the GC-native equivalent
     is the **benchmark curation loop**: 10–20 benchmarks with **required expected SQL** → run via
     the **Conversation API (`ask_genie`)** → diff → map each miss to the **5-mode fix table** →
     **append-only** fixes (skill Rule 17) → **re-run**, target **≥85%**. Ex3 prompts adopt the deck
     17a shape (Describe → Instructions → benchmarks-with-expected-answers) and bind to
     `genie-space-patterns` (Rules 12/17 + regression template) for the loop. `run-a`'s degradation
     was an *ad-hoc, unclosed* loop — the fix is to make it systematic, not to change surface.
  2. **Domains & Pages (Ex4/Ex5) = CORE chapters**, matching the deck, with explicit caveats: Pages
     is Beta, has **no public create/update API** (authored in the Discover UI with Genie Code
     assisting), and grounds **Genie One** (agent/GC integration is roadmap). Ex4 = domain +
     subdomains + author Pages (deck 22a); Ex5 = Routing Page (deck 26a).

**Revision (2026-09-13, r8) — Genie Ontology skill now exists + variable mapping corrected:**
- **New skill `semantic-layer/06-genie-discover-ontology`** backs Steps 11–13 (Ex4/Ex5): a thin
  **reference + drafting-contract** skill (no automation — Pages have no public create/update API, so
  Genie Code drafts in the Discover UI and a human publishes). Closes the earlier "skill gap." Numbered
  `06` to avoid colliding with the reserved `05` slot.
- **No new runtime variables** (corrected against the app repo): source =
  `{chapter_3_lakehouse_catalog/schema}` (`LakehouseParamsEditor`), write = `{lakehouse_default_catalog}`
  + `GoldTableTargetEditor`; metric-view name → Genie Code suggests; domain/subdomains → UI-first; BYO
  glossary/BI → uploaded. Step 1 reuses the existing extract/upload/generate mode-tab; Step 4 gets an
  Import BI tab with a promote-local→UC beat.

---

## 1. Purpose & goals

Revamp the app's **Genie Accelerator** track so that, starting from a user's existing data, a
participant is guided through an interactive, best-practice journey that ends in a **scored Genie
agent** — and, optionally, a full **platform activation** (dashboard → synced tables → Lakebase →
visualization app). The track is optimized for **Genie Code as the execution surface**.

**Success criterion:** a self-serve user, following only the app, produces a working,
benchmark-validated Genie agent on their own schema, understanding *why* at each step — and can
optionally continue to serve it to end users via the platform.

**Primary inputs that shaped this design:**
- The "Genie in a Bottle" hands-on workshop deck (curation-first philosophy, trust stack,
  `MEASURE()`, synonyms, benchmarks).
- The existing app (`vibe-coding-workshop-app`) — step/section model, `genie-accelerator` level,
  progressive-chain UX, use-case/PRD machinery, voice input.
- The existing template repo prompt system (`apps_lakebase/prompts/sections/*.md` →
  `02_seed_section_input_prompts.sql` → Lakebase → app), including the Genie Code forks
  (`*.genie-code.md`) and the `data_product_accelerator/skills/semantic-layer/` skills.

---

## 2. Design principles (locked)

1. **Spine = the automatable happy path.** The deck's concepts (trust stack, `MEASURE()`, synonyms,
   benchmarks, "curation > model") become the **teaching layer**, not scripted steps. We do **not**
   attempt to script Pages/Domains/Ontology or Workbench Auto-Optimize — those are surfaced as
   "next steps / manual in Genie One" because they have no create/update API and/or live in a
   separate surface today.
2. **Genie Code built-ins are the engine.** We lean on native skills (`using-metric-views`, SQL
   authoring, BI import, Genie space creation) and **wrap only at genuine gaps.**
3. **Our value is the thinking scaffold**, per best practice — "start small, curate what matters,
   plan before build."
4. **Interactivity is prompt-triggered.** Curated thin prompts make Genie Code
   *interview → propose → confirm*; the app does not simulate the chat.
5. **App = the runner** (initializer, big-picture map, prompt guide, "How it works" teaching).
   **Genie Code = the enabling executor** (incremental, interactive build).
6. **Adaptive entry with structured input.** Step 1 captures where the data is through the app's
   existing **structured** `LakehouseParams` panel (catalog.schema), so prompts arrive templated
   with the real names; if there is no data, a toggle routes to synthetic generation; the Gold
   layer is optional (recommend, don't force).
7. **Users bring their own definitions — primarily by handing files to Genie Code.** The primary
   BYO lane is Genie Code's native **file ingestion**: the user drops Excel glossaries, CSVs, docs,
   or BI exports into the repo (or attaches them) and Genie Code reasons on the *actual content*.
   `/importBI` handles Tableau / Power BI files → Metric Views. The app's FM-API attachment path is
   the *secondary, intent-stage* lane (turn a doc into a use-case description before Genie Code is
   open) — not the measure-reasoning path.
8. **Context spine persists and builds on the PRD.** The spine is `docs/design_prd.md` (use-case
   personas, *User Journeys*, *High-Level Data Entities*) → `docs/genie_brief.md` (the measures
   layer that *extends* the PRD) → `.vibecoding-state.md` (enter/exit gates + captured vars). Each
   step reads the PRD before asking the user anything the PRD already answers.
9. **Two reasoning surfaces, allocated by pedagogy (see §5.1).** The **app reasons about framing** —
   its FM API generates a personalized, ready-to-paste prompt for the **one** pure-intent beat, the
   **PRD** (the `prd_generation` meta-prompt pattern). **Genie Code reasons about content** — the
   real UC schema plus the files the user drops in — for **every downstream step**, which ships as a
   static template. Deck-sized prompts stay deck-sized; each is tagged **Type A** (app-generated,
   PRD only), **B** (template + variable substitution), or **C** (data-grounded / file-drop).
10. **Activation is optional but seamless** — it reuses the app's existing Activation chapter and is
    wired to the same context spine.

---

## 3. Architecture

```
APP (runner)                          GENIE CODE (enabling executor)
─────────────                         ──────────────────────────────
• Seeds intent (voice/form)           • Runs interview prompts
• Shows whole-journey map             • Elicits → proposes → builds
• Serves curated prompt per step      • Leans on native skills
• Teaches "How it works"     ───────▶ • Writes genie_brief.md + artifacts
• Tracks progress/gates               • enter/exit gates → .vibecoding-state.md
        ▲                                      │
        └──────────── context spine ───────────┘
          docs/genie_brief.md + .vibecoding-state.md (captured vars)
```

**Division of responsibility:**
- **App = "the runner":** initializer, big-picture map of the whole build, prompt guide, and the
  detailed "How it works" teaching surface. You stand here to see the *whole journey*.
- **Genie Code = "the enabling executor":** where the incremental, interactive work happens,
  driven by our curated Elicit → Propose → Build prompts.

**Context spine (the objects every step reads, in order):**
- `docs/design_prd.md` — **authored earlier in the journey** by the `prd_generation` step from the
  selected use case. Carries personas, *User Journeys*, scope, and *High-Level Data Entities*. The
  Genie track **reads it first** and does not re-ask what it already answers.
- `docs/genie_brief.md` — **extends** the PRD with the measures layer: function, ≤5 measures,
  one-sentence definitions, source-of-truth table/column, grain, owner, definition conflicts, the
  questions users actually ask, and the target tables. Seeded from the PRD + any BYO context.
- `.vibecoding-state.md` captured vars — `catalog`, `schema`/`gold_schema` (from the structured
  `LakehouseParams` entry), Metric View names, `genie_space_id`, `warehouse_id`, `dashboard_id`,
  `lakebase_*`.

**Structured input & BYO context (feed the spine):**
- **Structured schema location** — the entry card reuses the app's `LakehouseParams` API
  (`getLakehouseParams` / `updateLakehouseParams` / `autoSetLakehouseParamsFromLakebase`) and the
  `chapter_3_lakehouse_catalog` / `chapter_3_lakehouse_schema` session params; prompt templates pull
  them in by variable (as `22-genie_silver_metadata.md` already does).
- **BYO context — primary lane (Genie Code file ingestion)** — the user drops Excel / CSV / docs /
  BI exports into the repo (or attaches them via Genie Code's context button); prompts direct Genie
  Code to read + reason on the *actual content* and write what it learns into `genie_brief.md`. This
  is preferred because Genie Code reasons on the real file (no lossy app-side extraction), the file
  persists beside the brief, and there is no round-trip the app cannot do.
- **BYO context — BI-file special case (`/importBI`)** — native `/importBI` for `.twb/.twbx/.pbit`
  → Metric Views directly, surfaced as "Path A" in the Draft-Metric-View step.
- **BYO context — secondary lane (app FM-API attachment)** — `useCaseBuilderStream` /
  `processMetadataCsvStream` turn an upload into a **use-case description at the intent stage**
  (Step 0), before Genie Code is open. Not the measure-reasoning path.

This spine is how interactivity survives across steps and across **new Genie Code chat threads**:
each step re-reads the PRD, the brief, and the state file, so the agent always knows what the user
decided several steps ago.

---

## 4. Flow & step list (with acceptance gates — written test-first)

The acceptance gate for each step **is the test** — "done" means the gate passes on a live Genie
Code run. The section format already carries a `Gate` and `Expected Output`; we author those first.

Steps are grouped into **chapters** so the finer, deck-sized beats read as a coherent flow in the
runner rather than a flat list. Each numbered row is its own `section_tag` / prompt (its own
interactive beat), aligned to the deck's original prompt chunking (Ex1–Ex3).

| # | Step (app card) | Chapter | Reuses tag | Genie Code prompt (Elicit→Propose→Build) | Built-in leaned on | We wrap | **Acceptance gate** |
|---|---|---|---|---|---|---|---|
| 0 | **Define Intent** | on-ramp (app) | `usecase_selection` → `prd_generation` | *App-side*: function, industry, voice input; PRD authored to `docs/design_prd.md` | — (app) | use-case + PRD machinery | Intent captured; `docs/design_prd.md` exists |
| 1 | **Locate Data & Bring Context** | Discover | `genie_silver_metadata` + `LakehouseParams` | *App-side structured input*: pick `catalog.schema` (or "no data → synthetic"). *Genie Code (Type C template)*: "Read `docs/design_prd.md`; confirm the data location I captured; **read any files I dropped in**; seed the brief." | schema listing, Faker, Genie Code file-add | structured-input reuse + synthetic wrap + static file-drop template | `catalog.schema` saved to session `LakehouseParams` (or synthetic branch chosen); `design_prd.md` read; `genie_brief.md` seeded from PRD + any dropped files |
| 2 | **Profile Schema** | Discover | `genie_silver_metadata` | "Profile `<source_catalog>.<source_schema>`; produce an ERD; tell me what the schema can support today." (deck Ex1) | schema analysis | interview scaffold + brief format | ERD produced; schema-supportability noted in the brief — **⚠️ open decision (r6): in `run-a` this beat was absorbed into Steps 1 & 3 (no standalone ERD); decide whether to keep it explicit or fold the ERD ask into Step 1** |
| 3 | **Measures Analysis** *(new gate)* | Discover | *(new)* | "From the profile + PRD + my BYO context, draft a measures table — definition, source-of-truth, grain, owner, cross-team conflicts. Review with me. **No YAML yet.**" | FM-API draft (app pre-fills) | measures-analysis gate | Reviewed measures table in `genie_brief.md`; ≤5 measures each w/ definition + source + grain + owner; conflicts written; **user signs off before any Metric View YAML** |
| 4 | **Draft Metric View** | Semantic | *(split from `genie_space`)* | Per approved measure: propose YAML (grain, `MEASURE()`, non-additive flag) → review → author natively. **Path A:** `/importBI` a Tableau/PBI file to seed the MV. (deck Ex2·1) | `using-metric-views` + `/importBI` | best-practice checklist + validation | Each approved measure → 1 Metric View live; `MEASURE()` query returns; non-additive flagged |
| 5 | **Add Synonyms** | Semantic | *(split)* | "Add ≥3 synonyms per measure/dimension from my users' real vocabulary." (deck Ex2·2) | `using-metric-views` (MV `synonyms:` field) | synonym-coverage checklist | ≥3 synonyms per measure/key dimension in the **MV YAML** (`synonyms:`, v1.1) |
| 6 | **Add Verified Queries** | **Agent** *(moved from Semantic; runs after Step 7)* | `genie_space` | "Add the example queries the agent should reliably answer." (deck Ex2·3) | Genie space `instructions.example_question_sqls` | verified-query checklist | Verified Q→SQL examples on the **space** (not the MV); each `MEASURE()`-based; each returns |
| 7 | **Describe the Agent** | Agent | `genie_space` | "Describe the agent's job + scope in plain language; attach the Metric Views." (deck Ex3·1) | partial native | `serialized_space` contract + export/import (existing skill) | Space scaffold w/ description; MVs under `data_sources.metric_views`; `sql_functions` per TVF |
| 8 | **Author Instructions** | Agent | `genie_space` | "Write lean instructions ≤20 lines; climb the trust stack — context over rules." (deck Ex3·2) | native | instruction-budget checklist | Instructions ≤20 lines; no redundant/contradictory rules |
| 9 | **Draft Benchmarks** | Agent | `genie_space` | "Propose ≥10 benchmark questions from the brief; I correct the *expected answers*." → finalize space (deck Ex3·3) | partial native | benchmark gate + generation prompt | Space live; ≥10 benchmarks w/ SQL; runs a real question correctly |
| 10 | **Validate & Iterate** | Validate | `optimize_genie` | Run benchmarks → read failures → map each to a curation fix (failure→fix table) | native + optimize | existing skill | Benchmarks run; failures triaged to specific curation actions; accuracy reported (target is *guidance*, see §11 Q5) |
| 11 | **Dashboard** | Output | `aibi_dashboard` | AI/BI dashboard on the Metric Views | AI/BI native | thin pointer | Dashboard live; tiles query Metric Views |
| — | *seam: handoff recap + "+ Activate" invitation* | | | *Agent emits recap from captured vars; app offers the continuation* | | | Core track complete (a satisfying stop) |
| 12 | **Productionize as Asset Bundle** | Advanced (optional) | bundle skills (existing) | Wrap the already-authored files into a runnable DAB; `bundle validate`; run once in dev | — | bundle persistence | `databricks.yml` + resource jobs exist; `bundle validate` passes; jobs ran once in dev; live assets reproduce from files |
| 13 | **Synced Tables → Lakebase** | Activation (optional) | `activation_table_design`, `activation_reverse_sync`, `setup_lakebase` | Plan + create synced tables from the curated schema | ❌ not native | activation (existing) | Synced tables live in Lakebase |
| 14 | **Visualization App** | Activation (optional) | `activation_app_design`, `activation_build_wire`, `activation_wire_lakebase`, `activation_deploy_validate` | AppKit app over Lakebase; embeds Genie/dashboard | ❌ not native | AppKit reuse (existing) | App deployed & serving |
| C | **Clean Up** | close | `workspace_cleanup` | Tear down workshop resources | — | existing | Resources removed |

**Granularity note (r2, corrected r4):** the Metric-View beats (4 draft, 5 synonyms) and the Agent
beats (7 describe, 8 instructions, 9 benchmarks) are deliberately **separate beats**, mirroring the
deck's Exercise 2 and Exercise 3 chunking. **Verified queries (6)** moved from Semantic → Agent (r4:
they are a Genie-space feature, `example_question_sqls`, not a Metric View field) and run after the
space exists. The runner groups them under the **Semantic** and **Agent** chapters so the nav stays
legible while each beat keeps its own copy-able prompt. We are
adding interactivity + context to those deck prompts — not condensing them.

**Retirement note (Q2):** the current `genie-accelerator` step set
(`22 → 11 → 14 → 23 → 15 → 17 → 24 → 25`) is **retired and replaced** by the new 0–14 + Cleanup list
above. To avoid a broken half-state (see §10), the replacement ships as a `beta` level *beside* the
current one until Phase 4 passes, then flips to `enabled` and the old set is removed.

**Ordering note:** Validate (10) sits right after the agent beats (7–9) — it is agent-specific and
is the deck's "benchmark then believe" climax — with Dashboard (11) as the first tangible
"beyond-the-agent" output before the seam. The 10↔11 order is easily swappable (show the dashboard
before validating) if that reads better in testing.

**Split note (Q1):** the Semantic (4–6) and Agent (7–9) chapters are **separate cards**. The current
`genie_space` fork's "hybrid author → extract → bundle" logic is split accordingly: the
*author + native-apply* half stays in the core chapters (fast dev loop); the *bundle-persist* half
moves into step 12 (Productionize) — see §6.

---

## 5. Prompt structure (the "simpler, natural" contract)

Every step's `.genie-code.md` prompt follows a fixed, teachable shape:

```
[Goal — one plain sentence.]
[Context — "read docs/genie_brief.md and .vibecoding-state.md first."]

Before building anything:
 • Interview me on <the few things that matter here> — collect ALL open questions into ONE batched,
   numbered list (pre-fill your best assumption for each, marked "(assumed — correct me)"); don't
   drip questions one at a time.
 • Then show your plan/findings and STOP for my approval.

On approval, build it — using your native <skill> capability — and:
 • <the 2–3 best-practice rules that must hold> (e.g. wrap every measure in MEASURE()).
 • Update the brief/state and tell me what changed.
```

- **Thin & natural** on the surface; the guardrails that *must* be deterministic (the
  `serialized_space` contract, DAB persistence, `DP_BUNDLE_ROOT` anchoring) live in the **named
  wrapper skill**, pulled in by reference — not inlined into the prompt.
- The **gap map** (§6) decides, per step, whether a wrapper is named at all.
- The three-beat **Elicit → Propose → Build** shape is what reliably triggers Genie Code's
  interactivity. The "propose, then STOP for approval" gate is taken directly from the deck's
  repeated "ask for findings before artifacts" pattern.

### Worked example — Step 1 (Locate Data & Bring Context)

The `catalog.schema` is captured **app-side** via structured `LakehouseParams`; any data files are
handed to **Genie Code** directly (dropped into the repo or attached). This beat is **Type C** — a
static template with `catalog.schema` / `function` substituted in; Genie Code reasons on the real
schema and the files you drop in. (Only the upstream **PRD** is app-generated; see §5.1.) You paste:

```
Read docs/design_prd.md first — reuse its User Journeys and High-Level Data Entities;
don't re-ask what it already answers.

My data is in <catalog>.<schema>. (If I said I have none, offer to generate realistic
sample data for <function> and tell me the tradeoff.)

I've dropped my current definitions (an Excel glossary / a dashboard export) into the repo —
read them and pull the measure names and definitions you can from them.

Then, only for what the PRD + attachments don't cover, interview me — one question at a
time, wait for each answer:
 1. Which 3–5 measures do you check most? Stop me at five.
 2. For each: one-sentence definition, and which table/column is the source of truth?
 3. Where might two teams define the same measure differently?

Write/extend docs/genie_brief.md from the PRD + attachments + my answers. Do NOT create
Metric Views or a Genie space yet — show me the seeded brief for review.
```

Step 2 (Profile Schema) and Step 3 (Measures Analysis) then follow as their own beats — profiling
produces the ERD, and Measures Analysis produces the **reviewed measures table that gates all Metric
View YAML** (deck Ex1 "inventory" split out from Ex2 "author"). Steps 4–6 and 7–9 each carry one
deck prompt apiece.

### 5.1 Reasoning-surface allocation (App FM-API vs. Genie Code)

**Organizing principle:** *the app reasons about **framing**; Genie Code reasons about **content**.*
The app has only session context (industry, use case, `use_case_description`, params, prior
generated prompts), so it is the *prompt-smith* — it turns intent into a great, personalized prompt.
Genie Code has the repo files + the real data (UC schema, dropped files), so it is the *analyst and
builder*. The app never reads the user's repo or data; Genie Code never sees the app session. Each
step is exactly one of three types:

| Type | App mechanic | Who reasons | Use when |
|---|---|---|---|
| **A — App-authored prompt** (meta-prompt) | `bypass_llm=false`: the section `system_prompt` instructs the FM API to *generate a personalized prompt* from `use_case_description` + params + prior prompts. Output = a ready-to-paste Genie Code prompt. **The `prd_generation` pattern.** | App writes the prompt → Genie Code executes it | Framing/intent/discovery beats where personalization aids understanding and there is no real data to reason on yet |
| **B — Template prompt** | `bypass_llm=true`: variable substitution only (`{catalog}`, `{schema}`, `{function}`); text authored by us, stays exact | Genie Code | Guardrail-heavy build steps where correctness beats personalization (`serialized_space` contract, `MEASURE()` rules) |
| **C — Data-grounded prompt** | Same delivery as B, but the prompt directs the user to **drop files into Genie Code** and instructs it to read + reason on them | Genie Code, on real file content | Any step where the user's own definitions/data are the input — the primary BYO lane |

**Per-step allocation:**

| Step | Type | `bypass_llm` | App generates? | Genie Code reasons on |
|---|---|---|---|---|
| *PRD* (Step 0) | **A** | false | ✔ PRD-creation prompt (the **only** Type A step) | writes `design_prd.md` |
| 1 Locate + BYO | C | true | — | real schema + **dropped files** |
| 2 Profile | B | true | — | UC schema |
| 3 Measures Analysis | B → C | true | — | real profile + **dropped glossary** → table |
| 4 Draft MV (+`/importBI`) | B / C | true | — | signed-off measures + **BI file** |
| 5 Synonyms | B | true | — | the Metric View (`synonyms:`) + user vocabulary |
| 6 Verified queries *(Agent chapter)* | B | true | — | the Genie space (`example_question_sqls`) |
| 7 Describe agent | B | true | — | brief + `serialized_space` contract |
| 8 Instructions | B | true | — | the space |
| 9 Benchmarks | B | true | — | the Metric View |
| 10 Validate | B | true | — | benchmark results → failure→fix |
| 11 Dashboard | B | true | — | the Metric View |

**Deliberately one Type A step.** Only the **PRD** is app-generated. Everything the app *could*
personalize downstream — measures, conflicts, profiled columns — actually lives in the repo/data,
not the app session, so personalizing it app-side means *inventing* it. The realistic split is
therefore: the app generates the **PRD** (pure intent, no data yet), and every later step ships as a
**static template** (Type B) or a **file-drop template** (Type C) whose reasoning Genie Code does on
the real content (`design_prd.md`, the live schema, dropped files). Static templates are also what
Phase 2 encodes verbatim, so testing them now is a faithful preview. The app supplies the intent
frame once; Genie Code supplies all downstream discovery + build. This keeps the seam honest and the
prompts stable.

---

## 6. Skill / gap map (what we build vs. reuse)

| Capability | Genie Code native | Our contribution |
|---|---|---|
| Structured schema-location input | — (app) | **Reuse `LakehouseParams`** to capture **two** locations: a `{source_catalog}.{source_schema}` (existing data, Step 1 — may be read-only) **and** a `{write_catalog}.{write_schema}` (writable target for MV/space/dashboard). Layer-3 proved these differ (`samples.tpch` is read-only), so the write target is captured, never guessed |
| BYO context (**primary**): Excel / CSV / docs | ✅ Genie Code file-add | Prompts direct the user to drop files into Genie Code; it reasons on the real content → `genie_brief.md` (Type C) |
| BYO context (BI files): Tableau / Power BI | ✅ `/importBI` | Surface `/importBI` as "Path A" in Draft-Metric-View; point to `genie-space-patterns` / export-import skills |
| BYO context (secondary): app upload at intent | — (app FM-API) | `useCaseBuilderStream` / `processMetadataCsvStream` at **Step 0 only** — doc → `use_case_description` |
| Schema profiling / ERD | ✅ | Interview scaffold + brief format |
| Measures analysis (inventory before YAML) | — | **New gate**: reviewed measures table (definition, source-of-truth, grain, owner, conflicts); FM API pre-fills, user signs off before any MV YAML |
| Metric View authoring | ✅ `using-metric-views` | Best-practice checklist (`MEASURE()`, **synonyms** — MV `synonyms:` field, v1.1, ≤10 each — non-additive, format types); **snowflake joins work** (Layer-3 built 4-level nesting live) — **recommend** a pre-joined source subquery for multi-hop dims (simpler plan, parity-confirmed), nesting is a working fallback |
| TVFs | ✅ SQL | STRING-param / Genie-compat checklist (existing skill as CI reference) |
| Genie space create | ⚠️ shell only | `serialized_space` contract + export/import API (**existing skill**); `databricks genie create-space` needs a full `serialized_space` — the easy `table_identifiers` path is MCP-only |
| Verified / example queries | ✅ (Genie space) | Genie space `instructions.example_question_sqls` — **not** a Metric View field; authored *after* the space exists (Step 6, Agent chapter) |
| Benchmarks | ⚠️ | "answers are a guess — you verify" gate + generation prompt |
| AI/BI dashboard | ✅ | Thin pointer to Metric Views |
| Synced tables / Lakebase / App | ❌ | **Reuse existing Activation + AppKit sections** |
| Productionize as DAB (repeatable) | ❌ | Existing bundle skills — **optional step 12** |

**Dev-files-vs-prod-bundle boundary (Q3).** The core build steps and the productionize add-on draw
a clean line:

- **Core (steps 4–11): native-first, fast dev loop.** Artifacts are authored as **files** in the
  user project (`.sql` for TVFs, `.yaml` for Metric Views, `serialized_space` JSON for the Genie
  space) and applied with Genie Code's native tools. Nothing is a true *orphan* (a live asset with
  no file behind it) — the definitions are version-controllable files — but we do **not** pay the
  bundle/job tax yet. The point of the core is momentum: "see your agent answer a real question."
- **Add-on (step 12): productionize.** Wrap those already-authored files into a runnable **Asset
  Bundle** (`databricks.yml` + resource jobs), run `bundle validate`, and run the jobs once in dev.
  The semantic layer is now **reproducible and promotable** to staging/prod by `bundle deploy`
  alone.

**Placement & gating.** Step 12 sits **between** the core track and the Activation section, because
activation ("serve this for real") is the natural moment to want reproducibility first. It is a
**soft recommendation, not a hard prerequisite**: a user can technically sync + build the app on
the dev-applied assets, so the runner *strongly suggests* Productionize before Activation (and the
handoff recap explains why) but does not block it.

---

## 7. "How it works" teaching map (deck → step)

The deck's concepts become the app's per-step "How it works" content — the teaching layer that the
runner surfaces.

| Deck concept | Lands on | App surface |
|---|---|---|
| Curation > model; trust stack (8 levels) | Track intro + persistent sidebar | Interactive **trust-stack visual**, "you are here" |
| Bring your context (Excel / Tableau / PBI → definitions) | Step 1 | BYO-context uploader + `/importBI` explainer |
| Metrics discovery / start small / source-of-truth | Steps 1–2 | How-it-works panel + brief-completion tracker |
| Measure inventory before you model (analysis ≠ authoring) | Step 3 | **Measures-analysis table** (reviewed, gates YAML) |
| Why `MEASURE()` isn't optional; non-additive | Step 4 | Before/after "silent wrong number" callout |
| Synonyms = retrieval; OntoRank ties | Steps 5, 7–9 | Synonym-coverage explainer |
| Lean instructions / rich context; climbing the trust stack | Step 8 | Instruction-budget explainer |
| Benchmarks; "failures are the to-do list"; failure→fix table | Steps 9–10 | Interactive failure→fix table |
| Pages / Domains / Routing + Auto-Optimize | Track outro | "Next steps beyond Genie Code" (manual, Genie One) |

---

## 8. Interactivity

- **Prompt-triggered (primary):** the Elicit → Propose → Build shape in every step (§5).
- **App runner (secondary):** whole-journey map with the optional-seam divider; trust-stack
  "you are here"; brief-completion tracker; progress across gates; a generated handoff recap at the
  seam. Built on existing components (`WorkflowDiagram`, `ArchitectureDiagram`, `GalaxyMap`, guided
  tours).

---

## 9. Seamlessness of the optional activation tail

The activation tail already exists in the app as the Activation / Reverse-ETL chapter
(`activation_*` steps). We **reuse** it rather than authoring new build-the-app / Lakebase prompts,
wiring its inputs to the Genie track's captured vars. Five mechanisms keep it seamless for a
full-workshop attendee:

1. **One context spine, read by every step.** Activation steps read `genie_brief.md` +
   `.vibecoding-state.md` captured vars (`gold_schema`, Metric View names, `genie_space_id`,
   `warehouse_id`, `dashboard_id`) and never re-ask "which schema? which tables?" — the
   synced-tables plan is derivable straight from the brief's measures.
2. **Gate chaining across the boundary.** `require_prior_gate` links Dashboard-live →
   Productionize (soft) → Synced-tables → App-live. Activation can't start mis-sequenced, and
   stopping after the core is still a clean, complete finish.
3. **Reuse the app's progressive-chain UX.** Model this as `Genie Accelerator → + Activate`,
   identical to the existing `app-only → +Lakebase → +Lakehouse → +AI` cumulative climb
   (`PROGRESSION_CHAINS` + `getCumulativeOverrides`). The continuation feels native, not bolted on.
4. **The runner shows ONE map.** A single `WorkflowDiagram` with a soft divider —
   "Build your agent" | "Activate it on the platform" — with progress/completion spanning both.
   Optionality = the activation portion is deferred/collapsible, not a separate disjoint track.
5. **A generated handoff recap at the seam.** After the core, the agent (and the app card) emit a
   recap from captured vars: *"You built N Metric Views, a Genie space (`id…`), and a dashboard.
   Want to serve this to end users? Continue to sync into Lakebase and stand up an app."* That turns
   a stop into an intentional invitation.

Net: the core arc mirrors the deck and stays small; the activation module is existing content wired
to the same context spine, surfaced through the same chaining UX. A full-workshop attendee
experiences one continuous journey; someone stopping at the agent has a complete, satisfying result.

---

## 10. Validation & rollout plan

The guiding principle: **the product is the prompt behavior on Genie Code.** Everything else (seed
pipeline, app cards, how-it-works) is plumbing. So we front-load the risky validation and never sit
in a broken half-state.

- **Phase 0 — this spec, signed off.** Per-step gates (§4) are the tests.
- **Phase 1 — prove prompts on live Genie Code (a cheap spike).** Run the draft prompts for the
  core steps (1–11) by hand against **two representative schemas** — one with a clean Gold layer, one
  raw/needs-synthetic (exercises the adaptive gate) — and exercise BYO context both ways (**drop a
  file into Genie Code** and run `/importBI`) at least once. Iterate the text until each reliably
  (a) triggers the interview, (b) produces the artifact, (c) passes its gate. **Save the resulting
  Genie Code transcripts as golden references.** This de-risks ~80% of the project for ~a day.
- **Phase 2 — encode into the source-of-truth format, behind existing tooling.** Only now write the
  proven prompts into the section `.md` / `.genie-code.md` files. Run `lint_section_prompts.py`, the
  contract/baseline extractors, and the seed round-trip. Add **`scripts/verify_genie_track_flow.py`**
  — a CUJ verifier mirroring `scripts/verify_agent_track_flow.py`: it asserts the new ordered
  `section_tag` set, each row's `order_number`, key in-prompt content (e.g. Measures Analysis gates
  before MV YAML; Step 1 reads `design_prd.md`), and that the retired step set is gone. **Isolate the
  track** with its own section tags so the other ~14 levels can't regress; capture a contract
  baseline of the *before* state.
- **Phase 3 — app wiring, incrementally, additive.** Update `workflowSections.ts` for the new step
  list, the optional `+ Activate` chain, and the how-it-works content. Ship as **`beta`** using the
  existing `AcceleratorStatus` flag *beside* the current `genie-accelerator`. Extend the Playwright
  e2e (`hackathon-flow.spec.ts` pattern) with a runner walk.
- **Phase 4 — two independent full dogfood passes (the acceptance gate).** One person does the
  entire workshop on a fresh workspace using only the app (core, then activation). A **second person
  with fresh eyes** repeats. Two clean end-to-end passes, friction logged and fixed → done. Flip
  `beta → enabled` and remove the retired step set.

### "Done right" harness

| Level | Check | Exists already? |
|---|---|---|
| Per-step | The `Gate` passes on a live Genie Code run | ✅ gate pattern in sections |
| Per-step | Golden transcript matches expected behavior | New (Phase 1 artifact) |
| Type A (PRD only) | The app-generated PRD prompt is captured *separately* from the Genie Code transcript | New (Phase 1) |
| BYO | Genie Code reads a dropped CSV/Excel and reasons on it | New (Phase 1) |
| Discovery (realism) | Genie Code surfaces a measure conflict *unprompted* (not injected) — at Step 1 or Step 3; recorded in the signed-off inventory | New (Phase 1) |
| Prompt source | `lint_section_prompts.py` + contract baseline diff + seed round-trip | ✅ tooling in `apps_lakebase/prompts/` |
| Flow / CUJ | `verify_genie_track_flow.py` asserts the ordered step set + gates | New (mirrors `verify_agent_track_flow.py`) |
| App | Playwright e2e walks the track | ✅ e2e harness exists |
| Whole | Two independent full dogfood passes | New (Phase 4) |

### Shippable increments (no broken half-state)

1. Core arc (steps 1–11) fully validated and live first.
2. Activation module (steps 12–14) added as a second validated increment.

Additive + flagged: the new track lives beside the old under `beta` until Phase 4 passes, so `main`
is never broken for the other levels.

---

## 11. Resolved design decisions (Q1–Q5)

| # | Question | Decision |
|---|---|---|
| Q1 | Split Metric Views from Genie Agent, or keep the bundled `genie_space` step? | **Split** into separate chapters (Semantic = steps 4–6, Agent = steps 7–9). The `genie_space` fork's persistence logic splits too: author + native-apply in the core chapters, bundle-persist in step 12. |
| Q2 | Retire the current `genie-accelerator` step set or add the revamp beside it? | **Retire and replace.** Ship the replacement as `beta` beside the current one until Phase 4, then remove the old set. |
| Q3 | Is DAB persistence part of the default track or an add-on? | **Optional "advanced/production" add-on (step 12)**, placed between the core track and Activation, soft-recommended before serving to users. See the dev-files-vs-prod-bundle boundary in §6. |
| Q4 | Minimum synthetic-data path — reuse Faker or build a lighter variant? | **Reuse `bronze_layer_creation`/Faker as-is** for the synthetic path. |
| Q5 | Benchmark accuracy target — hard gate or guidance? | **Guidance** (deck's "aim ~85%, don't chase 100%"). The Validate gate requires benchmarks to run and failures to be triaged, not a specific accuracy number. |
| Q6 | How granular should the prompts be? | **Deck-sized chunks, not condensed.** Each deck prompt (Ex2 draft/synonyms/verified; Ex3 describe/instructions/benchmarks) is its own beat, grouped under the Semantic and Agent chapters. Interactivity + context are added *to* those prompts. |
| Q7 | Is `genie_brief.md` the PRD, or downstream of it? | **Downstream.** `genie_brief.md` **extends** the `prd_generation`-authored `docs/design_prd.md` (reuses its User Journeys + High-Level Data Entities); Step 1 reads the PRD first. |
| Q8 | How is the data location captured? | **Structured, app-side.** Reuse `LakehouseParams` + `chapter_3_lakehouse_*`; prompts template the real `catalog.schema`. A "no data → synthetic" toggle routes to Faker. |
| Q9 | How do users bring existing definitions? | **Primarily by handing files to Genie Code.** Drop Excel/CSV/docs into Genie Code — it reasons on the real content → brief (Type C); `/importBI` for Tableau/PBI → Metric Views. App-side upload is a secondary, **intent-stage** lane only (Step 0). |
| Q10 | How is reasoning split between the app and Genie Code? | **By pedagogy, per §5.1.** The app FM API generates a personalized prompt (**Type A**) for the **one** pure-intent beat — the **PRD**. Every downstream step ships as a **static template** (**Type B**) or **file-drop template** (**Type C**); Genie Code does all content reasoning on the real schema + dropped files. Deliberately one Type A step keeps the prompts stable and avoids the app inventing measures/conflicts it can't actually see. |

---

## 12. Related assets & references

- Workshop deck: "Genie in a Bottle — Hands-on Workshop" (curation philosophy, trust stack,
  Ex1–Ex3 prompt chunking, `/importBI` Path A).
- App: `vibe-coding-workshop-app` — `src/constants/workflowSections.ts` (`genie-accelerator` level,
  `PROGRESSION_CHAINS`, `getCumulativeOverrides`, `AcceleratorStatus`), use-case/PRD steps, voice
  input, `WorkflowDiagram`/`ArchitectureDiagram`/`GalaxyMap`.
- App structured input & FM-API surfaces (`src/api/client.ts`): `LakehouseParams` +
  `getLakehouseParams`/`updateLakehouseParams`/`autoSetLakehouseParamsFromLakebase` (structured
  schema location); `useCaseBuilderStream` (`text_attachments`/`pdf_attachments`/`images`) and
  `processMetadataCsvStream` (BYO-context ingestion via FM API); `generatePromptStream` (per-step
  personalization). Param mapping in `src/constants/workshopParamCategories.ts`.
- PRD spine: `apps_lakebase/prompts/sections/03-prd_generation.md` → `docs/design_prd.md`
  (User Journeys, High-Level Data Entities).
- Prompt system: `apps_lakebase/prompts/sections/*.md` and `*.genie-code.md` forks;
  `02_seed_section_input_prompts.sql`; `lint_section_prompts.py`; contract/baseline extractors;
  CUJ verifier precedent `scripts/verify_agent_track_flow.py` (→ new `verify_genie_track_flow.py`).
- Skills: `data_product_accelerator/skills/semantic-layer/` (metric-views-patterns,
  table-valued-functions, genie-space-patterns, genie-space-export-import-api,
  genie-optimization-orchestrator); `skills/vibecoding-state`; `skills/genie-code-environment`;
  `skills/databricks-asset-bundles`; AppKit skills under `apps_lakebase/skills/`.

---

## 13. Next step

Proceed to **Phase 1**: draft the deck-sized prompts for the core steps (1–11) and validate them on
live Genie Code against the two reference schemas (clean-Gold + raw/synthetic), exercising both
BYO-context lanes (attachment + `/importBI`) and the Measures-Analysis gate, saving golden
transcripts.
