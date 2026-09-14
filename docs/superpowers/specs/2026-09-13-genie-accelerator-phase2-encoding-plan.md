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

**Runtime variables** already substituted by the app (reuse these; don't invent parallels):
`{industry_name}`, `{use_case_title}`, `{use_case_description}`, `{lakehouse_default_catalog}`,
`{default_warehouse}`, `{prd_document}`, `{table_metadata}`, `{use_case_slug}`, `{databricks_cli_profile}`, …

**New variables this track needs** (add to the runtime substitution set + `LakehouseParams`):
`{source_catalog}.{source_schema}`, `{write_catalog}.{write_schema}`, `{metric_view}`, `{function}`,
`{domain}`, `{subdomain_*}`, `{byo_glossary_file}`.

---

## 2. Step → section mapping (the 18-step track)

Type → `bypass_llm`: **A = false** (FM-API generates), **B/C = true** (verbatim template).
"Fork?" = does it need a `genie-code` navigation fork on top of the DEFAULT row?

| Step | section_tag (proposed) | Type→`bypass_llm` | Fork? | Reuse / New | Binds to (skill) |
|---|---|---|---|---|---|
| 0 PRD | `prd_generation` *(existing)* | A → false | no | **REUSE** `03-prd_generation.md` | — |
| 1 Locate + BYO | `genieaccel_locate` | C → true | yes (file-drop, synthetic toggle) | NEW | `LakehouseParams`, Faker |
| 2 Profile | `genieaccel_profile` | B → true | no | NEW | `databricks-data-discovery` |
| 3 Measures gate | `genieaccel_measures` | B/C → true | no | NEW | design spec §4 gate |
| 4 Draft Metric View | `genieaccel_metric_view` | B/C → true | yes (`/importBI` Path A) | NEW | `using-metric-views`, `/importBI` |
| 5 Synonyms | `genieaccel_synonyms` | B → true | no | NEW | `using-metric-views` |
| 6 Describe agent | `genieaccel_agent_describe` | B → true | yes (createAsset/PATCH surface) | NEW | `03-genie-space-patterns` |
| 7 Instructions | `genieaccel_agent_instructions` | B → true | no | NEW | `03-genie-space-patterns` |
| 8 Verified queries | `genieaccel_verified_queries` | B → true | no | NEW | `03-genie-space-patterns` |
| 9 Load benchmarks | `genieaccel_benchmarks` | B → true | no | NEW | `03-genie-space-patterns` Rule 12 |
| 10 **Optimize loop** | `genieaccel_optimize` | B → true | yes (Conversation API run) | NEW *(cf. existing `optimize_genie`)* | `03-genie-space-patterns` Rule 17 |
| 11 Domain + subdomains | `genieaccel_domain` | B → true | yes (**Discover UI preferred** + pre-created fallback) | NEW | *(skill gap)* |
| 12 Author Pages | `genieaccel_pages` | B/C → true | yes (Discover UI Page editor) | NEW | *(skill gap)* |
| 13 Routing Page | `genieaccel_routing` | B → true | yes (Discover UI) | NEW | *(skill gap)* |
| 14 Share | `genieaccel_share` | B → true | no | NEW | — |
| 15 Dashboard *(tail)* | `genieaccel_dashboard` | B → true | yes (canvas navigation) | NEW *(cf. `aibi_dashboard`)* | AI/BI native |
| 16 Synced→Lakebase→App *(tail)* | `genieaccel_activation` | B → true | yes | NEW *(cf. `activation_*`)* | `databricks-lakebase`, `apps_lakebase` |
| 17 Productionize DAB *(tail)* | `genieaccel_dab` | B → true | yes (bundle-editor page) | NEW | `databricks-asset-bundles` |

Notes:
- **Step 0 reuses** the shipped PRD section unchanged — the track just points at it.
- **Steps 10/15/16 have existing cousins** (`optimize_genie`, `aibi_dashboard`, `activation_*`). Decide
  per the fork question below whether to reuse-and-enhance those tags or ship dedicated `genieaccel_*`
  tags for a clean, self-contained track.
- **Forks matter most at:** 1 (file-drop/synthetic), 4 (`/importBI`), 6 (createAsset/PATCH surface),
  10 (Conversation-API run), 11–13 (Discover UI), 15 (dashboard canvas), 17 (bundle-editor page) —
  everywhere the Genie Code *surface/navigation* differs from a generic assistant.

---

## 3. Order-number placement

The existing workflow occupies `order_number` 1–56 across five chapters. Two placement options
(the fork decision in §5):

- **Option A — dedicated track band.** Reserve a new band (e.g. `order_number` 60–77) for
  `genieaccel_*`, shown only when the "Genie Accelerator" track/use-case is selected (section
  visibility gating, same mechanism the Lakebase/Lakehouse chapters already use). Clean and
  self-contained; no risk to the existing flow.
- **Option B — weave into existing chapters.** Enhance `gold_layer_design` / `genie_space` /
  `optimize_genie` / `aibi_dashboard` / `activation_*` in place and add only the genuinely new
  sections (Measures gate, Domain, Pages, Routing). Less duplication, but touches shipped content and
  couples the track to the full 56-step flow.

---

## 4. Encoding sequence (once §5 is decided)

1. **Add the 7 new runtime variables** to the substitution set + a second `LakehouseParams` pair
   (source vs write target) — prerequisite for every template below.
2. **Batch 1 — Discover + Semantic (Steps 1–5):** author section files + DEFAULT INSERTs + genie-code
   forks for Locate, Profile, Measures, Metric View, Synonyms. (Highest-value, fully Phase-1-validated.)
3. **Batch 2 — Agent + Optimize (Steps 6–10):** Describe, Instructions, Verified queries, Benchmarks,
   Optimize loop.
4. **Batch 3 — Domains/Pages/Routing (Steps 11–13):** UI-preferred with pre-created fallback; carry
   the Beta caveats into `how_to_apply`. *(Author the missing Domains/Pages skill alongside.)*
5. **Batch 4 — Share + Activation tail (Steps 14–17):** optional-tail framing.
6. **"How it works"** content (deck-derived) for the app's explainer surface.
7. **Regression:** re-run `run-a`/`run-b` prompts against the *app-generated* text to confirm the
   encoded sections reproduce the validated prompts verbatim (Type B/C) or faithfully (Type A PRD).

Each batch = section `.md` files + seed INSERTs + forks, committed together, then diffed against the
Phase-1 golden transcripts in `phase1-evidence/`.

---

## 5. Open decision (needs your call before Batch 1)

**How should the track slot into the app's section workflow — Option A (dedicated `genieaccel_*` band,
gated) or Option B (weave into existing `gold`/`genie_space`/`optimize`/`activation` sections)?**
This determines the `section_tag` names and `order_number` band for all 17 rows, so it's the one
thing to settle before authoring section files.
