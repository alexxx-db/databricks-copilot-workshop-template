# Genie Accelerator — Phase 2 encoding plan (prompts → app sections)

**Status:** kickoff. Phase 1 validated the prompts on live Genie Code (`run-a` done; `run-b` prompts
staged in `phase1-evidence/run-b/_run-b-prompts.md`). Phase 2 encodes the finalized 18-step track
from `2026-09-13-genie-accelerator-phase1-prompts.md` into the app so the Configuration UI can
generate them.

---

## 1. How the app encodes a prompt (from `apps_lakebase/prompts/`)

Each workshop step is **one section**, defined in two coupled places:

1. **Section file** — `apps_lakebase/prompts/sections/NN-<section_tag>.md`, with YAML frontmatter
   (`input_id`, `section_tag`, `order_number`, `section_title`, `section_description`, `version`,
   `is_active`, `sql_comments`) + body (`## System Prompt`, `## Input Template`, `## How to Apply`,
   `## Expected Output`). This is the human-editable source.
2. **Seed INSERT** — a row in `apps_lakebase/prompts/02_seed_section_input_prompts.sql`
   (`input_id, section_tag, input_template, system_prompt, section_title, section_description,
   order_number, how_to_apply, expected_output, …`) that lands in `section_input_prompts`.

Key column = **`bypass_llm`**:
- `bypass_llm = false` → the section's **`system_prompt`** is sent to the app FM API, which **generates**
  a personalized, ready-to-paste prompt (the `prd_generation` pattern). **Type A.**
- `bypass_llm = true` → the **`input_template`** is used **verbatim** (variable substitution only).
  Genie Code does all the reasoning. **Type B / Type C.**

**Coding-assistant forks** (`sections/NN-<tag>.genie-code.md` → fork INSERT, `input_id` 1000+):
override only `input_template` / `system_prompt` / `bypass_llm` for `coding_assistant='genie-code'`.
Use a fork where the Genie Code surface needs **navigation guidance** the generic (Cursor/Copilot)
prompt shouldn't carry. Shared fields are always read from the DEFAULT row.

**Authoring workflow (source of truth = the `.md` section files):** edit/author
`sections/NN-<tag>.md`, then run **`apps_lakebase/prompts/sync_markdown_to_seed.py`** to regenerate
the matching INSERT(s) in `02_seed_section_input_prompts.sql` (`extract_to_markdown.py` is the
reverse direction; `sections/README.md` is an auto-generated index — don't hand-edit it). So a batch =
author `.md` files → run the sync → review the seed diff → `lint_section_prompts.py`.

> **Existing Genie-Accelerator band (sections 22–25) — review before authoring.** The app already
> ships a partial Genie-Accelerator flow: `genie_gold_design` (23, "Gold Layer Design (Genie
> Accelerator)"), `deploy_lakehouse_assets` (23), **`deploy_di_assets` (24, "Deploy Semantic Layer
> Assets (TVFs → Metric Views → Genie → Dashboard)")**, and `optimize_genie` (25). These are **deploy**
> steps (they push pre-planned assets), **not** the interactive *design* beats this track adds
> (Measures gate, Metric View authoring, synonyms review). The new **Semantic Layer** section is the
> *design* front-end that feeds these deploy steps — author it to hand off cleanly. (Step-10 optimize
> is the GC-native curation loop in its own `gagent_optimize` section; `optimize_genie` (25) stays as
> the heavyweight Workbench-style option — see §2.)

**Runtime variables** already substituted by the app (reuse these; don't invent parallels):
`{industry_name}`, `{use_case_title}`, `{use_case_description}`, `{lakehouse_default_catalog}`,
`{chapter_3_lakehouse_catalog}`, `{chapter_3_lakehouse_schema}`, `{default_warehouse}`,
`{prd_document}`, `{table_metadata}`, `{use_case_slug}`, `{databricks_cli_profile}`, …

**No new runtime variables are required** (corrected 2026-09-13 after inspecting the app repo — the
substitution set + structured inputs already cover this track). Map the track's needs onto what
exists:

| Track need | Use existing | App input surface |
|---|---|---|
| Source catalog/schema (read) | **`{chapter_3_lakehouse_catalog}` / `{chapter_3_lakehouse_schema}`** ("Lakehouse Source Catalog/Schema", per-session overridable) | `LakehouseParamsEditor` (label `Source:`; `allow_session_override`) |
| Write catalog/schema (governed assets) | **`{lakehouse_default_catalog}`** (write catalog) + schema/prefix | `GoldTableTargetEditor` (catalog + schema + prefix) — note there is **no** `lakehouse_default_schema` param; the write schema lives in the Gold-target editor |
| Metric View name | **none** — Genie Code suggests it | — |
| Function / team | **derive** from `{use_case_title}` / `{industry_name}` / `{use_case_description}` | existing use-case context |
| Domain / subdomains | **none** — UI-first (Discover UI) | Discover UI |
| BYO glossary / BI file | **none** — uploaded (chat drop / UC volume / CSV panel) | `CsvUploadPanel` / Genie Code file-add / `/importBI` |

> **The "second LakehouseParams pair" already exists.** Source = `LakehouseParamsEditor`; write =
> `GoldTableTargetEditor`. No new pair, no new tokens — the earlier "add 7 vars + a pair" prerequisite
> is retracted.

---

## 2. Step → section mapping (RESOLVED placement)

**Decision (2026-09-13):** *"Put domains, sub-domains, pages into a new track for **Genie Ontology**.
Spread the rest between Genie Space, Optimize Genie, AI/BI Dashboard, Activate, etc. For Metric Views
/ Measures, review if there's an existing semantic-layer section — there isn't — so **create a new
Semantic Layer section** and put them there."*

Verified against the seed: **no** semantic-layer section exists today (Metric Views appear only inside
`usecase_plan` and `aibi_dashboard`); `genie_space`, `optimize_genie`, `aibi_dashboard`, and
`activation_*` all exist and are reused/enhanced in place.

Type → `bypass_llm`: **A = false** (FM-API generates), **B/C = true** (verbatim template).
"Fork?" = needs a `genie-code` navigation fork on top of the DEFAULT row.

| Step | section_tag | Home | Type→`bypass_llm` | Fork? | New / Reuse | Binds to (skill) |
|---|---|---|---|---|---|---|
| 0 PRD | `prd_generation` | *(existing)* | A → false | no | **REUSE** unchanged | — |
| 1 Locate + BYO | `semlayer_locate` | **Semantic Layer (NEW)** | C → true | yes (file-drop, synthetic toggle) | NEW | `LakehouseParams`, Faker |
| 2 Profile | `semlayer_profile` | **Semantic Layer (NEW)** | B → true | no | NEW | `databricks-data-discovery` |
| 3 Measures gate | `semlayer_measures` | **Semantic Layer (NEW)** | B/C → true | no | NEW | design spec §4 gate |
| 4 Draft Metric View | `semlayer_metric_view` | **Semantic Layer (NEW)** | B/C → true | yes (`/importBI` Path A) | NEW | `using-metric-views`, `/importBI` |
| 5 Synonyms | `semlayer_synonyms` | **Semantic Layer (NEW)** | B → true | no | NEW | `using-metric-views` |
| 6 Describe agent | `gagent_describe` | **Genie Agent (NEW track)** | B → true | yes (createAsset/PATCH) | NEW | `03-genie-space-patterns` |
| 7 Instructions | `gagent_instructions` | **Genie Agent (NEW track)** | B → true | no | NEW | `03-genie-space-patterns` |
| 8 Verified queries | `gagent_verified` | **Genie Agent (NEW track)** | B → true | no | NEW | `03-genie-space-patterns` |
| 9 Load benchmarks | `gagent_benchmarks` | **Genie Agent (NEW track)** | B → true | no | NEW | `03-genie-space-patterns` Rule 12 |
| 10 **Optimize loop** | `gagent_optimize` | **Genie Agent (NEW track)** | B → true | yes (Conversation API run) | NEW *(GC-native; ≠ `optimize_genie`)* | `03-genie-space-patterns` Rule 17 |
| 11 Domain + subdomains | `ontology_domain` | **Genie Ontology (NEW track)** | B → true | yes (**Discover UI preferred** + pre-created fallback) | NEW | `semantic-layer/06-genie-discover-ontology` |
| 12 Author Pages | `ontology_pages` | **Genie Ontology (NEW track)** | B/C → true | yes (Discover UI Page editor) | NEW | `semantic-layer/06-genie-discover-ontology` |
| 13 Routing Page | `ontology_routing` | **Genie Ontology (NEW track)** | B → true | yes (Discover UI) | NEW | `semantic-layer/06-genie-discover-ontology` |
| 14 Share | `gagent_share` | **Genie Agent (NEW track)** | B → true | no | NEW | — |
| 15 Dashboard *(tail)* | `aibi_dashboard` | **AI/BI Dashboard (reuse)** | B → true | optional fork | REUSE / hand-off | AI/BI native |
| 16 Synced→Lakebase→App *(tail)* | `activation_*` | **Activation (reuse)** | B → true | — | REUSE / hand-off | `databricks-lakebase`, `apps_lakebase` |
| 17 Productionize DAB *(tail)* | `deploy_di_assets` / `activation_*` | **DAB deploy band (reuse)** | B → true | — | REUSE / hand-off | `databricks-asset-bundles` |

Notes:
- **Modality decision (2026-09-13):** the existing `genie_space` (15) / `deploy_di_assets` (24) /
  `optimize_genie` (25) band is the **manifest-driven, DAB-deploy** modality (assumes the full
  `data_product_accelerator` pipeline + `plans/manifests/*.yaml`). The Genie Accelerator track is the
  **conversational, BYO-schema, Genie-Code-native** modality. **We do NOT enhance the manifest band
  in place** — the two co-exist. Steps 1–13 are authored as the track's **own new gated sections**
  (three groups: `semlayer_*`, `gagent_*`, `ontology_*`); the manifest band stays intact as the
  optional **"productionize via DAB"** hand-off the Activation tail points to.
- **New content = 13 sections in three groups:** **Semantic Layer** `semlayer_*` (Steps 1–5),
  **Genie Agent** `gagent_*` (Steps 6–10, 14), **Genie Ontology** `ontology_*` (Steps 11–13).
- **Steps 1–2 placement.** Locate + Profile lead the Semantic Layer group (the discovery arc that
  *produces* the measures), so the group reads "data → measures → metric view → synonyms."
- **Step 1 reuses an existing UI pattern (don't reinvent).** The app's Step 10 (`bronze_table_metadata`)
  already ships a **three-mode tab** — `extract` (from tables, via `LakehouseParamsEditor` = source
  catalog/schema), `upload` (`CsvUploadPanel`), `generate` ("Design from PRD" = the **synthetic /
  no-existing-tables** branch). `semlayer_locate` should reuse this exact extract/upload/generate mode
  tab; the "read existing OR synthetic" toggle you want already exists as `generate` mode.
- **Step 4 needs an Import BI tab (own mode), and Import BI creates MORE than a Metric View.**
  `/importBI` (Tableau `.twb/.twbx/.tds/.tdsx`, Power BI `.pbit`; ≤100 MB direct or a UC volume path)
  builds an **AI/BI dashboard + LOCAL (dashboard-scoped) metric views + relationships** — the local
  views are **not reusable** and must be **promoted to UC** ("Export to Metric View" →
  `{lakehouse_default_catalog}` + Gold-target schema) before the Genie Agent can use them. A cleaner
  "import the data model only" path starts the import from an empty UC metric view. So `semlayer_metric_view`
  should offer **Tab A — author from the measures inventory** (Path B) and **Tab B — Import BI** with an
  explicit **promote-local→UC** beat. Docs: <https://docs.databricks.com/aws/en/dashboards/manage/import-bi>.
- **Step 10 optimize is GC-native and distinct** from `optimize_genie` (25): the lighter Conversation-
  API benchmark-curation loop (5-mode table → append-only → ~85%), not the MLflow/8-scorer/6-lever
  orchestrator. `optimize_genie` (25) stays as the heavyweight Workbench-style option (currently
  `step_enabled: false`).
- **Tail (15–17) is a hand-off, not new authoring:** after the conversational build, a user who wants
  manifests + bundle deploy flows into the existing `deploy_di_assets` (24) / `activation_*`. Add only
  a light genie-code fork on `aibi_dashboard` if the dashboard-on-Metric-View beat needs it.
- **Forks matter most at:** 1 (file-drop/synthetic), 4 (`/importBI`), 6 (createAsset/PATCH), 10
  (Conversation-API run), 11–13 (Discover UI).

---

## 3. Order-number placement (RESOLVED)

Existing workflow occupies `order_number` 1–56. The Genie Accelerator track is a **self-contained
gated band** (visibility-gated to the track selection, the same mechanism optional chapters use), so
it does not renumber the linear flow. Proposed reserved band `order_number` **60–73**:

- **Semantic Layer** `semlayer_*` — 60–64 (Locate, Profile, Measures, Metric View, Synonyms)
- **Genie Agent** `gagent_*` — 65–69 (Describe, Instructions, Verified queries, Benchmarks, Optimize)
- **Genie Ontology** `ontology_*` — 70–72 (Domain, Pages, Routing) — after Optimize (deck: Ex3 → Ex4/Ex5)
- **Share** `gagent_share` — 73
- **Tail (15–17)** reuses existing `deploy_di_assets` (24) / `aibi_dashboard` (14) / `activation_*`
  (32–37) at their current `order_number`s — reached as an optional hand-off, not renumbered.

Exact numbers confirmed against the app's track/visibility-gating when Batch 1 is authored.

---

## 4. Encoding sequence

0. **[DONE] Reviewed the existing band** (`genie_space` 15, `deploy_di_assets` 24, `optimize_genie`
   25): confirmed manifest-driven/DAB modality — kept intact as the productionize hand-off, NOT
   enhanced. Steps 1–13 authored as the track's own gated sections.
1. **~~Add 7 runtime variables + a second LakehouseParams pair~~ — RETRACTED (no new vars needed).**
   Instead: **map** the track templates onto existing tokens — source =
   `{chapter_3_lakehouse_catalog}` / `{chapter_3_lakehouse_schema}` (`LakehouseParamsEditor`), write =
   `{lakehouse_default_catalog}` + Gold-target editor. Metric-view name, domain/subdomains, and BYO
   files are not variables (Genie Code suggests / UI-first / uploaded). See §1 mapping table.
2. **[DONE 2026-09-14] Batch 1 — Semantic Layer group (Steps 1–5, NEW):** authored `semlayer_*`
   section files (`order_number` 60–64, `input_id` 60–64) + two genie-code forks (`input_id` 932/933:
   Locate file-drop/synthetic navigation, Metric View `/importBI` Path A). All seven parsed into the
   seed and **pass `lint_section_prompts.py`**. `semlayer_locate` (Step 1) reuses the
   extract/upload/generate mode-tab pattern; `semlayer_metric_view` (Step 4) carries the Path A
   Import-BI + promote-local→UC beat (Tab A author / Tab B Import BI). See §5 decision log for the two
   tooling findings surfaced during encoding.
3. **[DONE 2026-09-14] Batch 2 — Genie Agent group (Steps 6–10, 14, NEW):** authored `gagent_*`
   sections (`order_number`/`input_id` 65–69, 73: Describe, Instructions, Verified queries, Benchmarks,
   GC-native Optimize loop, Share) + two genie-code forks (`input_id` 934/935: Describe
   createAsset/PATCH navigation, Optimize Conversation-API loop). All eight scoped-synced into the seed
   and **pass `lint_section_prompts.py`**. Prompt bodies are the Phase-1-validated Steps 6–10/14
   verbatim; Step 10 optimize is the GC-native curation loop, distinct from `optimize_genie` (25).
4. **[DONE 2026-09-14] Batch 3 — Genie Ontology group (Steps 11–13, NEW):** authored `ontology_*`
   sections (`order_number`/`input_id` 70–72: Domain, Pages, Routing) + three genie-code forks
   (`input_id` 936/937/938), UI-preferred with the pre-created-domain fallback and Beta caveats in
   `how_to_apply`. All six scoped-synced and **pass `lint_section_prompts.py`**. *(The Ontology skill
   already exists — `data_product_accelerator/skills/semantic-layer/06-genie-discover-ontology`, the
   REFERENCE + DRAFTING-CONTRACT skill — so no skill needed authoring; the sections point at it. The
   earlier "skill gap" note was stale.)*
5. **Batch 4 — Tail hand-off (Steps 15–17):** wire the track's close to the existing
   `deploy_di_assets` (24) / `aibi_dashboard` (14) / `activation_*`; add a light `aibi_dashboard`
   genie-code fork only if the dashboard-on-Metric-View beat needs it. No new monolith authoring.
6. **"How it works"** content (deck-derived) for the app's explainer surface.
7. **Regression:** re-run `run-a`/`run-b` prompts against the *app-generated* text to confirm encoded
   sections reproduce the validated prompts verbatim (Type B/C) or faithfully (Type A PRD).

Each batch = section `.md` files + seed INSERTs + forks, committed together, diffed against the
Phase-1 golden transcripts in `phase1-evidence/`.

---

## 5. Decision log

- **2026-09-13 — placement (§2, superseded):** initial split had Agent/Optimize *enhancing*
  `genie_space` / `optimize_genie` in place.
- **2026-09-13 — modality RECONCILED after reviewing the band (§2, current):** the existing
  `genie_space` (15) / `deploy_di_assets` (24) / `optimize_genie` (25) band is manifest-driven +
  DAB-deploy — a different modality from the conversational, GC-native track. Decision: **author
  Steps 1–13 as the track's own new gated sections** in three groups (`semlayer_*`, `gagent_*`,
  `ontology_*`) and **leave the manifest band intact** as the optional productionize hand-off (tail
  Steps 15–17). Step 10 optimize is the GC-native curation loop, distinct from `optimize_genie` (25).
- **2026-09-14 — Batch 1 encoded (§4.2):** authored `sections/60–64-semlayer_*.md` (DEFAULT,
  `bypass_llm=true`) + `sections/99-semlayer_{locate,metric_view}.genie-code.md` (forks, `input_id`
  932/933). Tokens mapped per §1: source `{chapter_3_lakehouse_catalog}.{chapter_3_lakehouse_schema}`,
  write `{lakehouse_default_catalog}.{user_schema_prefix}_gold`, function `{use_case_title}`. Prompt
  bodies are the Phase-1-validated Steps 1–5 verbatim. All seven `✅` under `lint_section_prompts.py`.
- **2026-09-14 — Batch 3 encoded (§4.4):** authored `sections/70–72-ontology_*.md` (DEFAULT,
  `bypass_llm=true`, UI-preferred) + `sections/99-ontology_{domain,pages,routing}.genie-code.md`
  (forks, `input_id` 936/937/938). Parser now sees 114 blocks; all six `✅` under
  `lint_section_prompts.py` (0 new errors). **Corrected a stale plan note:** the Ontology skill
  `06-genie-discover-ontology` already exists (Beta limits, Manage-Discovery, chunk-safe rule,
  ID-vs-name gotcha) — sections reference it; nothing new to author. Discover has no public Pages API,
  so all three are UI-first with Genie-Code drafting inside the editor. Same gitignore/working-copy
  caveat.
- **2026-09-14 — Batch 2 encoded (§4.3):** authored `sections/65–69,73-gagent_*.md` (DEFAULT,
  `bypass_llm=true`) + `sections/99-gagent_{describe,optimize}.genie-code.md` (forks, `input_id`
  934/935). Same token mapping and scoped-sync approach as Batch 1; parser now sees 108 blocks; all
  eight `✅` under `lint_section_prompts.py` (0 new lint errors). Verified queries correctly land on the
  space (`instructions.example_question_sqls`), not the Metric View; benchmarks require expected SQL per
  item; the optimize fork uses `ask_genie` + append-only 5-mode fixes. Same gitignore caveat as Batch 1
  (files are a working copy; canonical home = `vibe-coding-workshop-app`).
- **2026-09-14 — TWO tooling findings surfaced during Batch 1 (action needed before Batch 2 commit):**
  1. **`apps_lakebase/prompts/` is gitignored in THIS repo** (`.gitignore:96`) — zero files tracked.
     The encoded `.md` + seed are a **working copy**; the canonical, version-controlled home is the
     **`vibe-coding-workshop-app` repo**. Batch-1 artifacts must be landed there to persist (only this
     tracked `docs/` plan captures the work in the template repo).
  2. **`sync_markdown_to_seed.py` is non-idempotent against the current seed** — a full run wants to
     rewrite **all 100 blocks** (global `.md`↔seed formatting drift, pre-existing). So the documented
     "author `.md` → run sync → review diff" flow can NOT be run wholesale without sweeping unrelated
     churn. Batch 1 used a **scoped sync** (reusing `build_insert_block`/`parse_markdown` filtered to
     the 7 new ids) + hand-seeded stub rows. Before Batch 2: either re-baseline the seed from all
     `.md` in a dedicated commit, or keep using the scoped-sync approach per batch.
- **2026-09-13 — variables RETRACTED after inspecting the app repo (§1):** no new runtime variables or
  a "second LakehouseParams pair" are needed. Source = `{chapter_3_lakehouse_catalog/schema}`
  (`LakehouseParamsEditor`, per-session override); write = `{lakehouse_default_catalog}` + the
  `GoldTableTargetEditor` (there is no `lakehouse_default_schema` param). Metric-view name → Genie Code
  suggests; domain/subdomains → UI-first; BYO glossary/BI → uploaded. **Step 1 reuses the existing
  Step-10 extract/upload/generate mode-tab pattern** (synthetic = `generate`). **Import BI creates an
  AI/BI dashboard + LOCAL metric views + relationships** — Step 4 gets an Import BI tab with an
  explicit **promote-local→UC** beat.
