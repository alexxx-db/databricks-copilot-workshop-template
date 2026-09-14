# Steps 5–10 — Synonyms → Space → Instructions → Verified Queries → Benchmarks → Validate  (Run A)

- **Date / operator:** 2026-09-13 / prashanth.subrahmanyam
- **Write target:** `serverless_stable_6t92c3_catalog.revenuescope`

## What worked well (keep)

- **Step 4 rebuild (pre-joined source):** parity EXACT vs nested-join version (all 5 measures + region×year slice). Confirms the snowflake correction.
- **Step 5 (synonyms):** review/expand worked — 34 synonyms across 16 columns (acronyms, persona language, disambiguation labels), ≤10 cap respected. The "review, don't add-from-scratch" reframe matched reality.
- **Step 7 (space):** Genie space created on the **governed Metric View only** (no raw tables), verified via `askGenieSpace` — all 11 dimensions + 5 measures visible.
- **Step 8 (instructions):** guardrails from brief §7 applied as lean rules; GC cut formulas + data-fact percentages (correct — those aren't routing rules).
- **Step 6 (verified queries):** 3 example_question_sqls saved **to the space** (one per persona), each `MEASURE()`-based and executed. Confirms verified queries live on the space, not the MV.

## ⚠️ Degradations vs the "Genie in a Bottle" deck (REVERSE these)

1. **Agent built on the Genie Code path with NO optimizer.** The deck's Exercise 3 builds the agent
   in **Workbench** and **launches Auto-Optimize** (baseline 61% → 88% is the whole payoff). The
   deck names Genie Code an explicit *fallback* that "loses the scoring and the optimizer." Our track
   made the fallback the default and dropped the optimizer.
2. **Step 10 became manual "run each benchmark, show the SQL."** The deck's validation is
   **benchmark → Auto-Optimize → read accuracy → map failures to the 5-mode fix table → accept/reject
   optimizer changes → re-run**, targeting ≥85%. Our hand-rolled loop is strictly weaker and skips
   the product's optimization feature. *(Operator note: the optimization is a real feature that
   triggers when the prompt calls for it the workshop way — load benchmarks w/ expected answers, then
   optimize — not by asking GC to execute queries one by one.)*
3. **Exercises 4 & 5 (Domains + Pages) dropped entirely.** The deck treats domain modeling, Pages
   (disambiguation/guardrail/routing), and the routing Page as core curation. We deferred them. They
   ground Genie One and remove whole classes of wrong-table failures. (Caveat: Pages is Beta, no
   public create/update API — authored in the Discover UI with Genie Code assisting.)
4. **Drift from deck wording / over-scaffolding** in a few spots — snap back to the deck's prompts.

## Verdict

The **Discover → Metric View** half (Ex1–Ex2) is strong and matches the deck. The **Agent → Validate**
half (Ex3 + Part 7) degraded by dropping Workbench Auto-Optimize, and **Ex4–Ex5 are missing**. The
finalized plan (spec r7) re-anchors to the deck with an explicit enhancement whitelist.
