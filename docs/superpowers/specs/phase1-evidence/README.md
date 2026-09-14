# Phase 1 evidence — Genie Accelerator track (live Genie Code golden references)

This folder holds the **golden transcripts + state deltas** from running the Phase-1 prompt drafts
by hand on live Genie Code. Phase 2 encodes the section files against these references.

Companion docs:
- Prompts + runbook: `../2026-09-13-genie-accelerator-phase1-prompts.md`
- Design spec: `../2026-09-13-genie-accelerator-track-design.md` (§5.1 reasoning-surface, §10 harness)

## How to run (make it as realistic as production)

1. **Run in the real environment.** Drive Genie Code in-workspace, not a mimic. The one exception is
   Step 0's PRD prompt, which is *app-generated* — obtain it from the app (or a faithful FM-API call
   on `apps_lakebase/prompts/sections/03-prd_generation.md`) and save it verbatim as the Step-0
   artifact.
2. **Open with `vibecoding-state`.** Start each run with the `vibecoding-state` bootstrap/`enter`
   (resolves `artifact_root`, loads `client_context`, creates/loads `.vibecoding-state.md`). Close
   with `exit`.
3. **Use the static templates verbatim.** Steps 1–11 are copied exactly from the prompts doc with
   only `catalog.schema` / `function` / `{byo_glossary_file}` substituted. **Inject nothing else** —
   especially no measures or conflicts.
4. **Bring a real file.** For BYO, drop the user's *own* glossary/export (`{byo_glossary_file}`) into
   Genie Code — do not fabricate one. Run B exercises `/importBI` with a real `.twbx`/`.pbit`.
5. **Capture per step.** Copy one `_step-template.md` per step into `run-a/` or `run-b/`, fill it,
   and paste the transcript + the `.vibecoding-state.md` diff.

## Runs

| Run | Schema | BYO lane | Folder |
|---|---|---|---|
| A | Clean-Gold (e.g. `samples.tpch`) | file-add (`{byo_glossary_file}`) | `run-a/` |
| B | Raw / needs-synthetic (Faker) | `/importBI` at Step 4 | `run-b/` |

## Acceptance checklist (every run must pass all)

- [ ] **Type A capture (PRD only):** the app-generated PRD prompt is saved separately (`step-00-prd.md`); Steps 1–11 used verbatim static templates.
- [ ] **PRD spine:** Step 1 transcript quotes `design_prd.md` User Journeys / Data Entities instead of re-asking.
- [ ] **BYO file-add:** Genie Code reads the dropped `{byo_glossary_file}`; ≥1 brief definition is traceable to it (with citation).
- [ ] **Measures-Analysis gate:** Step 3 shows the reviewed table and **no** Metric View YAML; Step 4 proceeds only after an explicit sign-off line.
- [ ] **⭐ Unprompted conflict discovery:** no prompt named a conflict, yet the transcript shows Genie Code surfacing ≥1 on its own — **at Step 1 (elicitation) OR Step 3 (inventory)**; if raised at Step 1, Step 3 must still record it in the signed-off table. *(Headline realism check — if the conflict was in the prompt, the run is invalid.)*
- [ ] **State persistence:** `.vibecoding-state.md` accumulates each step's gate result across the run (not reset per prompt).
- [ ] **BYO `/importBI` (Run B):** a Metric View originates from the import payload; field aliases survive as synonyms in Step 5.
- [ ] **Non-additive protection:** Step 4 flags the non-additive measure; Steps 6/8 protect it with `MEASURE()`.

## What to compare against

- Behavioral expectations per step: the "Golden transcript should show" line in each step of the prompts doc.
- Numeric/answer key (Clean-Gold only): Appendix A of the prompts doc — the grader's key, **never a prompt input**.
