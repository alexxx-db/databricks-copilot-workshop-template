# Genie Accelerator Track — Design Spec

**Status:** Design-complete (Phase 0). Ready to drive Phase 1 (prompt drafting + live validation).
**Date:** 2026-09-13
**Scope:** Revamp of the app's `genie-accelerator` workshop track, optimized for Genie Code as the execution surface.

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
6. **Adaptive entry.** Step 1 asks where the data is; offers synthetic data generation if none;
   the Gold layer is optional (recommend, don't force).
7. **Context spine persists** via `.vibecoding-state.md` (enter/exit gates + captured vars) and
   `docs/genie_brief.md`.
8. **Activation is optional but seamless** — it reuses the app's existing Activation chapter and is
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

**Context spine (the object every step reads):**
- `docs/genie_brief.md` — function, 3–5 measures, one-sentence definitions, source-of-truth,
  definition conflicts, the questions users actually ask, and the target tables.
- `.vibecoding-state.md` captured vars — `catalog`, `gold_schema`, Metric View names,
  `genie_space_id`, `warehouse_id`, `dashboard_id`, `lakebase_*`.

This spine is how interactivity survives across steps and across **new Genie Code chat threads**:
each step re-reads the brief and the state file, so the agent always knows what the user decided
several steps ago.

---

## 4. Flow & step list (with acceptance gates — written test-first)

The acceptance gate for each step **is the test** — "done" means the gate passes on a live Genie
Code run. The section format already carries a `Gate` and `Expected Output`; we author those first.

| # | Step (app card) | Bucket | Reuses tag | Genie Code prompt (Elicit→Propose→Build) | Built-in leaned on | We wrap | **Acceptance gate** |
|---|---|---|---|---|---|---|---|
| 0 | **Define Intent** | on-ramp (app) | `usecase_selection` | *App-side*: function, industry, voice input | — (app) | use-case machinery | Intent captured |
| 1 | **Data + Measures Brief** | Core | `prd_generation` + `genie_silver_metadata` | "Where's your data? Interview me on ≤5 measures, sources, conflicts, user questions." → writes `genie_brief.md`, profiles schema, produces ERD. *If no data → offers synthetic Bronze.* | schema analysis, Faker | adaptive-profiling + synthetic-data wrap | `genie_brief.md` exists; ≤5 measures each with definition + source + owner; ERD produced; schema-supportability noted; user approved |
| 2 | **Metric Views** | Core | *(new; split from `genie_space`)* | Per measure: propose YAML (grain, `MEASURE()`, synonyms ≥3, non-additive flag) → review → author natively | `using-metric-views` | best-practice checklist + validation | Each brief measure → 1 Metric View live; `MEASURE()` query returns; synonyms present; non-additive flagged |
| 3 | **Genie Agent** | Core | `genie_space` | Propose ≥10 benchmarks from brief (user corrects *expected answers*) + lean instructions ≤20 lines → create space | partial native | `serialized_space` contract + export/import (existing skill) | Space live; ≥10 benchmarks w/ SQL; MVs under `data_sources.metric_views`; `sql_functions` per TVF; runs a real question correctly |
| 4 | **Validate & Iterate** | Core | `optimize_genie` | Run benchmarks → read failures → map each to a curation fix (failure→fix table) | native + optimize | existing skill | Benchmarks run; failures triaged to specific curation actions; accuracy reported (target is *guidance*, see §11 Q5) |
| 5 | **Dashboard** | Core | `aibi_dashboard` | AI/BI dashboard on the Metric Views | AI/BI native | thin pointer | Dashboard live; tiles query Metric Views |
| — | *seam: handoff recap + "+ Activate" invitation* | | | *Agent emits recap from captured vars; app offers the continuation* | | | Core track complete (a satisfying stop) |
| 6 | **Productionize as Asset Bundle** | Advanced (optional) | bundle skills (existing) | Wrap the already-authored files into a runnable DAB; `bundle validate`; run once in dev | — | bundle persistence | `databricks.yml` + resource jobs exist; `bundle validate` passes; jobs ran once in dev; live assets reproduce from files |
| 7 | **Synced Tables → Lakebase** | Activation (optional) | `activation_table_design`, `activation_reverse_sync`, `setup_lakebase` | Plan + create synced tables from the curated schema | ❌ not native | activation (existing) | Synced tables live in Lakebase |
| 8 | **Visualization App** | Activation (optional) | `activation_app_design`, `activation_build_wire`, `activation_wire_lakebase`, `activation_deploy_validate` | AppKit app over Lakebase; embeds Genie/dashboard | ❌ not native | AppKit reuse (existing) | App deployed & serving |
| C | **Clean Up** | close | `workspace_cleanup` | Tear down workshop resources | — | existing | Resources removed |

**Retirement note (Q2):** the current `genie-accelerator` step set
(`22 → 11 → 14 → 23 → 15 → 17 → 24 → 25`) is **retired and replaced** by the new 0–8 + Cleanup list
above. To avoid a broken half-state (see §10), the replacement ships as a `beta` level *beside* the
current one until Phase 4 passes, then flips to `enabled` and the old set is removed.

**Ordering note:** Validate (4) sits right after Genie Agent (3) — it is agent-specific and is the
deck's "benchmark then believe" climax — with Dashboard (5) as the first tangible
"beyond-the-agent" output before the seam. The 4↔5 order is easily swappable (show the dashboard
before validating) if that reads better in testing.

**Split note (Q1):** Metric Views (2) and Genie Agent (3) are **separate cards**. The current
`genie_space` fork's "hybrid author → extract → bundle" logic is split accordingly: the
*author + native-apply* half stays in steps 2–3 (fast dev loop); the *bundle-persist* half moves
into step 6 (Productionize) — see §6.

---

## 5. Prompt structure (the "simpler, natural" contract)

Every step's `.genie-code.md` prompt follows a fixed, teachable shape:

```
[Goal — one plain sentence.]
[Context — "read docs/genie_brief.md and .vibecoding-state.md first."]

Before building anything:
 • Interview me on <the few things that matter here>, one question at a time.
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

### Worked example — Step 1 (Data + Measures Brief)

```
I want a Genie agent that answers questions about <function> from data I already have.

First: where does that data live? If I don't have it yet, offer to generate realistic
sample data for <function> and tell me the tradeoff.

Then interview me — one question at a time, wait for each answer:
 1. What decisions do you make each week from this data?
 2. Which 3–5 measures do you check most? Stop me at five.
 3. For each: one-sentence definition, and which table/file is the source of truth?
 4. Where might two teams define the same measure differently?
 5. What do users actually ask, in their words?

Then write docs/genie_brief.md, profile <catalog>.<schema>, produce an ERD, and tell me
which measures the schema can support today. Do NOT create Metric Views or a Genie space
yet — show me the brief and findings for review.
```

---

## 6. Skill / gap map (what we build vs. reuse)

| Capability | Genie Code native | Our contribution |
|---|---|---|
| Schema profiling / ERD | ✅ | Interview scaffold + brief format |
| Metric View authoring | ✅ `using-metric-views` | Best-practice checklist (`MEASURE()`, synonyms, non-additive, format types) |
| TVFs | ✅ SQL | STRING-param / Genie-compat checklist (existing skill as CI reference) |
| Genie space create | ⚠️ shell only | `serialized_space` contract + export/import API (**existing skill**) |
| Benchmarks | ⚠️ | "answers are a guess — you verify" gate + generation prompt |
| AI/BI dashboard | ✅ | Thin pointer to Metric Views |
| Synced tables / Lakebase / App | ❌ | **Reuse existing Activation + AppKit sections** |
| Productionize as DAB (repeatable) | ❌ | Existing bundle skills — **optional step 6** |

**Dev-files-vs-prod-bundle boundary (Q3).** The core build steps and the productionize add-on draw
a clean line:

- **Core (steps 2–5): native-first, fast dev loop.** Artifacts are authored as **files** in the
  user project (`.sql` for TVFs, `.yaml` for Metric Views, `serialized_space` JSON for the Genie
  space) and applied with Genie Code's native tools. Nothing is a true *orphan* (a live asset with
  no file behind it) — the definitions are version-controllable files — but we do **not** pay the
  bundle/job tax yet. The point of the core is momentum: "see your agent answer a real question."
- **Add-on (step 6): productionize.** Wrap those already-authored files into a runnable **Asset
  Bundle** (`databricks.yml` + resource jobs), run `bundle validate`, and run the jobs once in dev.
  The semantic layer is now **reproducible and promotable** to staging/prod by `bundle deploy`
  alone.

**Placement & gating.** Step 6 sits **between** the core track and the Activation section, because
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
| Metrics discovery / start small / source-of-truth | Step 1 | How-it-works panel + brief-completion tracker |
| Why `MEASURE()` isn't optional; non-additive | Step 2 | Before/after "silent wrong number" callout |
| Synonyms = retrieval; OntoRank ties | Steps 2–3 | Synonym-coverage explainer |
| Lean instructions / rich context; climbing the trust stack | Step 3 | Instruction-budget explainer |
| Benchmarks; "failures are the to-do list"; failure→fix table | Step 4 | Interactive failure→fix table |
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
- **Phase 1 — prove prompts on live Genie Code (a cheap spike).** Run the draft interview prompts
  for steps 1–5 by hand against **two representative schemas** — one with a clean Gold layer, one
  raw/needs-synthetic (exercises the adaptive gate). Iterate the text until each reliably
  (a) triggers the interview, (b) produces the artifact, (c) passes its gate. **Save the resulting
  Genie Code transcripts as golden references.** This de-risks ~80% of the project for ~a day.
- **Phase 2 — encode into the source-of-truth format, behind existing tooling.** Only now write the
  proven prompts into the section `.md` / `.genie-code.md` files. Run `lint_section_prompts.py`, the
  contract/baseline extractors, and the seed round-trip. **Isolate the track** with its own section
  tags so the other ~14 levels can't regress; capture a contract baseline of the *before* state.
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
| Prompt source | `lint_section_prompts.py` + contract baseline diff + seed round-trip | ✅ tooling in `apps_lakebase/prompts/` |
| App | Playwright e2e walks the track | ✅ e2e harness exists |
| Whole | Two independent full dogfood passes | New (Phase 4) |

### Shippable increments (no broken half-state)

1. Core arc (steps 1–5) fully validated and live first.
2. Activation module (steps 6–8) added as a second validated increment.

Additive + flagged: the new track lives beside the old under `beta` until Phase 4 passes, so `main`
is never broken for the other levels.

---

## 11. Resolved design decisions (Q1–Q5)

| # | Question | Decision |
|---|---|---|
| Q1 | Split Metric Views from Genie Agent, or keep the bundled `genie_space` step? | **Split** into separate cards (steps 2 and 3). The `genie_space` fork's persistence logic splits too: author + native-apply in 2–3, bundle-persist in step 6. |
| Q2 | Retire the current `genie-accelerator` step set or add the revamp beside it? | **Retire and replace.** Ship the replacement as `beta` beside the current one until Phase 4, then remove the old set. |
| Q3 | Is DAB persistence part of the default track or an add-on? | **Optional "advanced/production" add-on (step 6)**, placed between the core track and Activation, soft-recommended before serving to users. See the dev-files-vs-prod-bundle boundary in §6. |
| Q4 | Minimum synthetic-data path — reuse Faker or build a lighter variant? | **Reuse `bronze_layer_creation`/Faker as-is** for the synthetic path. |
| Q5 | Benchmark accuracy target — hard gate or guidance? | **Guidance** (deck's "aim ~85%, don't chase 100%"). The Validate gate requires benchmarks to run and failures to be triaged, not a specific accuracy number. |

---

## 12. Related assets & references

- Workshop deck: "Genie in a Bottle — Hands-on Workshop" (curation philosophy, trust stack).
- App: `vibe-coding-workshop-app` — `src/constants/workflowSections.ts` (`genie-accelerator` level,
  `PROGRESSION_CHAINS`, `getCumulativeOverrides`, `AcceleratorStatus`), use-case/PRD steps, voice
  input, `WorkflowDiagram`/`ArchitectureDiagram`/`GalaxyMap`.
- Prompt system: `apps_lakebase/prompts/sections/*.md` and `*.genie-code.md` forks;
  `02_seed_section_input_prompts.sql`; `lint_section_prompts.py`; contract/baseline extractors.
- Skills: `data_product_accelerator/skills/semantic-layer/` (metric-views-patterns,
  table-valued-functions, genie-space-patterns, genie-space-export-import-api,
  genie-optimization-orchestrator); `skills/vibecoding-state`; `skills/genie-code-environment`;
  `skills/databricks-asset-bundles`; AppKit skills under `apps_lakebase/skills/`.

---

## 13. Next step

Proceed to **Phase 1**: draft the interview prompts for steps 1–5 and validate them on live Genie
Code against the two reference schemas (clean-Gold + raw/synthetic), saving golden transcripts.
