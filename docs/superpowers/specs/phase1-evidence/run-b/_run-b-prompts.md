# Run B — raw / needs-synthetic schema + BYO via `/importBI` (live Genie Code prompt sequence)

Run B proves the **two branches Run A did not exercise**:
1. **Synthetic branch** — the user has *no usable data*, so Step 1 offers Faker-generated sample data
   for `{function}` (the adaptive branch in the design spec §4 / `bronze_layer_creation` + Faker).
2. **BYO via `/importBI`** — instead of dropping a glossary file, the user imports a **Tableau/Power BI**
   semantic model at Step 4 (Genie Code native `/importBI`), and its field aliases must survive as
   Metric View synonyms in Step 5.

Everything else is **identical to Run A**: same static templates (Steps 1–3, 5–14), same gates, same
`vibecoding-state` wrapper, same Measures-Analysis gate, same Step-10 optimize loop, same Ex4/Ex5.
Only Step 1 and Step 4 change. Capture each step with a copy of `../_step-template.md` into `run-b/`.

---

## Scenario (concrete fills — swap for your own)

| Variable | Run B value |
|---|---|
| `{function}` | Subscription revenue reporting |
| `{source_catalog}.{source_schema}` | *(none — synthetic)* → generate into `{write_catalog}.{write_schema}` |
| `{write_catalog}.{write_schema}` | `serverless_stable_6t92c3_catalog.genie_accel_runb` |
| `{metric_view}` | `subscription_revenue_metrics` |
| BYO lane | `/importBI` with a real `.twbx` or `.pbit` at Step 4 |
| `{domain}` | `Subscription Analytics` (or the workshop's pre-created domain) |

> Pick a **real** BI file you own for `/importBI`. Do not fabricate one — the whole point of Run B is
> that the import is genuine (its field aliases are the evidence in Step 5).

---

## State bootstrap (run once, verbatim — same as Run A)

```
Using skills/vibecoding-state: resolve_root, then bootstrap/enter the session for the Genie
Accelerator track. Resolve <ARTIFACT_ROOT> (my user project root, a git clone of the workshop repo —
NOT the .assistant/skills copy, NOT the page CWD), load client_context, and create or load
<ARTIFACT_ROOT>/.vibecoding-state.md. Confirm the resolved artifact_root and client_context back to
me, then stop.
```

## Step 0 — PRD (Type A, app-generated)

Same as Run A: obtain the PRD prompt from the app (or a faithful FM-API mimic on
`apps_lakebase/prompts/sections/03-prd_generation.md`) for a **subscription revenue** use case; run
it; save the emitted prompt verbatim as `step-00-prd.md`. Gate: `docs/design_prd.md` exists.

---

## ⭐ Step 1 — Locate Data & Bring Context — **SYNTHETIC BRANCH** (the Run-B delta)

The user has no usable data, so this prompt **omits the `catalog.schema` line** and instead asks
Genie Code to offer synthetic data. (App-side: the user toggled "No data → synthetic".)

```
Read docs/design_prd.md and .vibecoding-state.md first — reuse the PRD's User Journeys and
High-Level Data Entities; don't re-ask what they already answer.

I don't have usable source data for subscription revenue reporting yet. Offer to generate realistic
sample data for it: propose the tables, their grain, and roughly how the tables join (base it on the
PRD's High-Level Data Entities), tell me the tradeoff of synthetic vs. real data, and only generate
it if I say yes. Build the sample data into serverless_stable_6t92c3_catalog.genie_accel_runb.

Start docs/genie_brief.md from the PRD: function, candidate measures, and the questions my users
actually ask. If anything the PRD doesn't cover needs my input, collect ALL of it into ONE numbered
list of questions and ask me in a single batch — do not drip them one at a time. Pre-fill your best
assumption for each and mark it "(assumed — correct me)". Do NOT build anything yet — show me the
proposed sample-data plan plus the seeded brief and that one question list, and record the gate
result in .vibecoding-state.md.
```

**Golden transcript should show:** Genie Code reads the PRD, proposes a synthetic schema grounded in
the PRD's Data Entities, states the tradeoff, **waits for a yes** before generating, seeds
`genie_brief.md`, and asks ONE batched question list. After you approve, it Faker-generates the
tables into the write target. *(This is the adaptive synthetic branch — the gate is "sample-data
plan approved + brief seeded", not "catalog.schema saved".)*

> After approval, a follow-up prompt to actually build it:
> ```
> Yes, generate the sample data as proposed. Use Faker for realistic values, keep referential
> integrity across the tables, and confirm row counts per table when done. Then STOP — do not build a
> Metric View yet.
> ```

## Step 2 — Profile Schema  *(now runs against the just-generated synthetic schema)*

Same template as Run A, with `<source_catalog>.<source_schema>` =
`serverless_stable_6t92c3_catalog.genie_accel_runb` (the synthetic schema you just built). Produce
the ERD; note per-measure supportability.

## Step 3 — Measures Analysis  *(the gate — identical template to Run A)*

Same verbatim template. **Realism check still applies:** the template names no conflict; Genie Code
must surface any it finds from the synthetic profile on its own, and the inventory stops at five.

---

## ⭐ Step 4 — Draft the Metric View — **`/importBI` PATH A** (the Run-B delta)

Instead of authoring from scratch (Run A's Path B), import the BI semantic model. **Know what
`/importBI` actually produces:** it does **not** just make a Metric View — it builds an **AI/BI
dashboard + LOCAL (dashboard-scoped) metric views + discovered relationships**. The local views are
**not reusable by a Genie Agent**, so you must **promote** the one(s) you want to Unity Catalog first.
(≤100 MB direct, or a UC volume path for larger files. Docs:
<https://docs.databricks.com/aws/en/dashboards/manage/import-bi>.)

1. In Genie Code, run **`/importBI`** and upload your real `.twbx` / `.twb` / `.tds` / `.tdsx` / `.pbit`.
2. Review what it produced — a dashboard + local metric view(s). **Do not promote all of them**; keep
   only the view covering your signed-off inventory (Step 3).
3. **Promote local → UC:** "Export to Metric View" into
   `serverless_stable_6t92c3_catalog.genie_accel_runb` so the Genie Agent can attach it.
4. Then:

```
Read docs/genie_brief.md (the signed-off inventory) and .vibecoding-state.md first.

I ran /importBI, which created an AI/BI dashboard plus local (dashboard-scoped) metric views. Promote
ONLY the view covering my signed-off inventory to Unity Catalog and save it as
@serverless_stable_6t92c3_catalog.genie_accel_runb.subscription_revenue_metrics using CREATE OR REPLACE
(check state + the target schema for an existing one of this name first). Keep only the measures in my
inventory and drop the rest. Use business-friendly display names, flag any non-additive measure, and
run a MEASURE() query to prove each approved measure returns. Keep the imported field aliases — I'll
turn them into synonyms next. Then save the Metric View name and gate result to .vibecoding-state.md.
```

**Golden transcript should show:** `/importBI` produces a dashboard + local metric view(s); exactly
one is **promoted to a governed UC Metric View**; non-inventory measures are dropped; a `MEASURE()`
query returns; and the **imported field aliases are retained** for Step 5. *(Bulk-import misses
usually mean the domain **name** was passed where the internal **ID** is needed.)*

## Step 5 — Review & Expand Synonyms  *(BI aliases must survive here)*

Same template as Run A. **Run-B-specific gate:** at least one synonym on the Metric View traces back
to a **`/importBI` field alias** — this is the BYO-`/importBI` acceptance check.

---

## Steps 6–14 — identical to Run A

Describe agent (6) → Instructions (7) → Verified queries on the space (8) → Load benchmarks with
expected SQL (9) → **Optimize loop: run → fix → re-run (10)** → Domain + subdomains, UI-preferred /
pre-created (11) → Author Pages (12) → Routing Page (13) → Share (14). Use the verbatim templates in
`../2026-09-13-genie-accelerator-phase1-prompts.md` with the Run-B fills above.

---

## Run-B acceptance (in addition to the shared checklist in `../README.md`)

- [ ] **Synthetic branch:** Step 1 offered synthetic data, stated the tradeoff, **waited for a yes**,
      then Faker-built the tables into the write target with referential integrity + row counts.
- [ ] **`/importBI`:** a Metric View originated from a **real** imported `.twbx`/`.pbit`; non-inventory
      measures were dropped.
- [ ] **BI aliases → synonyms:** ≥1 synonym in Step 5 traces to an imported field alias.
- [ ] **Gates hold + optimize loop closes** exactly as Run A (Step 3 gate, Step 10 re-run pass rate).
- [ ] **Ex4/Ex5 published** (domain UI-preferred / pre-created; two Pages + one Routing Page).
