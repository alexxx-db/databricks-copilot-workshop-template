# Step 2 — Profile Schema  (Run A)

- **Date / operator:** 2026-09-13 / prashanth.subrahmanyam
- **Type:** B (static template)
- **Status:** **ABSORBED — the standalone Step 2 prompt was not run.**

## What happened

Genie Code profiled the schema **inline** during Step 1 (mapping PRD entities to `samples.tpch`
tables while seeding the brief) and again during Step 3 (inspecting real data to surface measure
conflicts). The operator went Step 1 → 3 open questions → Step 3 → Step 4 and **never pasted the
standalone Step 2 "Profile Your Schema" prompt**. No explicit ERD artifact was produced.

## Realism finding (open decision)

The standalone Profile beat may be redundant when Step 1 already triggers schema inspection. Two
options to fold into the design spec §4:
1. **Keep Step 2 explicit** — it's the deck's Ex1 "Profile Your Schema" beat and produces the ERD;
   maybe Step 1 should *not* profile so Step 2 has a distinct job.
2. **Fold "produce an ERD" into Step 1** and drop Step 2 as a standalone.

Not auto-resolved — flagged for the operator. Everything downstream (Step 3 measures, Step 4 MV) still
worked without the standalone profile, so this is a flow-tightening question, not a defect.
