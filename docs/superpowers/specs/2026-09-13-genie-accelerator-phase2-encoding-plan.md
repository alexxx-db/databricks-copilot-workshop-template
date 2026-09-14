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
> *design* front-end that feeds these deploy steps — author it to hand off cleanly, and **reuse
> `optimize_genie` (25)** as the Step-10 optimize home rather than duplicating it.

**Runtime variables** already substituted by the app (reuse these; don't invent parallels):
`{industry_name}`, `{use_case_title}`, `{use_case_description}`, `{lakehouse_default_catalog}`,
`{default_warehouse}`, `{prd_document}`, `{table_metadata}`, `{use_case_slug}`, `{databricks_cli_profile}`, …

**New variables this track needs** (add to the runtime substitution set + `LakehouseParams`):
`{source_catalog}.{source_schema}`, `{write_catalog}.{write_schema}`, `{metric_view}`, `{function}`,
`{domain}`, `{subdomain_*}`, `{byo_glossary_file}`.

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
| 6 Describe agent | `genie_space` | **Genie Space (reuse)** | B → true | yes (createAsset/PATCH) | ENHANCE | `03-genie-space-patterns` |
| 7 Instructions | `genie_space` | **Genie Space (reuse)** | B → true | no | ENHANCE | `03-genie-space-patterns` |
| 8 Verified queries | `genie_space` | **Genie Space (reuse)** | B → true | no | ENHANCE | `03-genie-space-patterns` |
| 9 Load benchmarks | `genie_space` | **Genie Space (reuse)** | B → true | no | ENHANCE | `03-genie-space-patterns` Rule 12 |
| 10 **Optimize loop** | `optimize_genie` | **Optimize Genie (reuse)** | B → true | yes (Conversation API run) | ENHANCE | `03-genie-space-patterns` Rule 17 |
| 11 Domain + subdomains | `ontology_domain` | **Genie Ontology (NEW track)** | B → true | yes (**Discover UI preferred** + pre-created fallback) | NEW | *(skill gap)* |
| 12 Author Pages | `ontology_pages` | **Genie Ontology (NEW track)** | B/C → true | yes (Discover UI Page editor) | NEW | *(skill gap)* |
| 13 Routing Page | `ontology_routing` | **Genie Ontology (NEW track)** | B → true | yes (Discover UI) | NEW | *(skill gap)* |
| 14 Share | `genie_space` (close) | **Genie Space (reuse)** | B → true | no | ENHANCE | — |
| 15 Dashboard *(tail)* | `aibi_dashboard` | **AI/BI Dashboard (reuse)** | B → true | yes (canvas nav) | ENHANCE | AI/BI native |
| 16 Synced→Lakebase→App *(tail)* | `activation_*` | **Activation (reuse)** | B → true | yes | ENHANCE | `databricks-lakebase`, `apps_lakebase` |
| 17 Productionize DAB *(tail)* | `activation_*` | **Activation (reuse)** | B → true | yes (bundle-editor page) | ENHANCE | `databricks-asset-bundles` |

Notes:
- **New content = 8 sections in two homes:** the **Semantic Layer** section (Steps 1–5) and the
  **Genie Ontology** track (Steps 11–13). Everything else *enhances* an existing section in place.
- **Steps 1–2 placement.** Locate + Profile are the discovery arc that *produces* the measures, so
  they lead the Semantic Layer section. (Alternative: fold them into `gold_layer_design` — left in
  Semantic Layer so the track reads as one "data → measures → metric view" story. Revisit if the app
  already gates a discovery step ahead of this.)
- **Enhance-in-place discipline.** For `genie_space` / `optimize_genie` / `aibi_dashboard` /
  `activation_*`, layer the validated wording in as **additive** changes (append example beats /
  genie-code forks); do not rewrite shipped prompts wholesale — diff against the Phase-1 goldens.
- **Forks matter most at:** 1 (file-drop/synthetic), 4 (`/importBI`), 6 (createAsset/PATCH), 10
  (Conversation-API run), 11–13 (Discover UI), 15 (dashboard canvas), 17 (bundle-editor page).

---

## 3. Order-number placement (RESOLVED)

Existing workflow occupies `order_number` 1–56. Placement per the decision:

- **Semantic Layer section (Steps 1–5)** — a new section band sequenced with the data/semantic work:
  slot it just **after Gold** and **before `genie_space`** (so measures → metric view precede the
  agent). Candidate band `order_number` ~13.x–13.z (between `gold_layer_pipeline` and `genie_space`)
  or a reserved 60–64 band if visibility-gating keeps it out of the full linear flow.
- **Genie Ontology track (Steps 11–13)** — a new gated track, own band (e.g. `order_number` 70–72),
  shown when the ontology track is selected; sequenced **after Optimize** (deck order: Ex3 optimize →
  Ex4/Ex5 ontology).
- **Enhanced sections (6–10, 14–17)** keep their existing `order_number`s — only `input_template` /
  `system_prompt` / genie-code forks change.

Exact numbers finalized when the section files are authored (Batch 1), matching the app's visibility-
gating for optional chapters.

---

## 4. Encoding sequence

0. **Review the existing 22–25 band** (`genie_gold_design`, `deploy_lakehouse_assets`,
   `deploy_di_assets`, `optimize_genie`) so the new Semantic Layer *design* beats hand off to the
   existing *deploy* beats without duplication, and Step 10 reuses `optimize_genie`.
1. **Add the 7 new runtime variables** to the substitution set + a second `LakehouseParams` pair
   (source vs write target) — prerequisite for every template below.
2. **Batch 1 — Semantic Layer section (Steps 1–5, NEW):** author `semlayer_*` section files, run
   `sync_markdown_to_seed.py`, add genie-code forks (Locate, Profile, Measures, Metric View,
   Synonyms). Highest-value, fully Phase-1-validated, and the cleanest new home.
3. **Batch 2 — Enhance Genie Space + Optimize (Steps 6–10):** additively layer Describe / Instructions
   / Verified queries / Benchmarks into `genie_space`, and the closed optimize loop into
   `optimize_genie` (+ Share close on `genie_space`).
4. **Batch 3 — Genie Ontology track (Steps 11–13, NEW):** `ontology_*` sections, UI-preferred with the
   pre-created-domain fallback; Beta caveats in `how_to_apply`. *(Author the missing Ontology skill
   alongside — the current repo skill gap.)*
5. **Batch 4 — Enhance Activation tail (Steps 15–17):** additive genie-code forks on `aibi_dashboard` /
   `activation_*`.
6. **"How it works"** content (deck-derived) for the app's explainer surface.
7. **Regression:** re-run `run-a`/`run-b` prompts against the *app-generated* text to confirm encoded
   sections reproduce the validated prompts verbatim (Type B/C) or faithfully (Type A PRD).

Each batch = section `.md` files + seed INSERTs + forks, committed together, diffed against the
Phase-1 golden transcripts in `phase1-evidence/`.

---

## 5. Decision log

- **2026-09-13 — placement RESOLVED (§2):** Genie Ontology = new gated track (domains/subdomains/
  pages/routing). Semantic Layer = new section for Locate→Synonyms (Measures + Metric Views live here
  since no semantic-layer section existed). Agent/Optimize/Dashboard/Activation = enhance the existing
  `genie_space` / `optimize_genie` / `aibi_dashboard` / `activation_*` sections in place.
