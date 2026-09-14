# Step 1 — Locate Data & Bring Context  (Run A)

- **Date / operator:** 2026-09-13 / prashanth.subrahmanyam
- **Type:** C (static file-drop template) — run **without** a glossary (pure-discovery pass)
- **Schema:** `samples.tpch`
- **BYO file:** none (BYO lines deleted, as the template allows)

## Prompt used (verbatim)

```
Read docs/design_prd.md and .vibecoding-state.md first — reuse the PRD's User Journeys and
High-Level Data Entities; don't re-ask what they already answer.

My data for order & revenue reporting is in samples.tpch.

Start docs/genie_brief.md from the PRD (+ any dropped files): function, candidate measures, and the
questions my users actually ask. Elicit anything the PRD and files don't cover — one question at a
time. Do NOT profile deeply or build anything yet — show me the seeded brief so I can correct it,
and record the gate result in .vibecoding-state.md.
```

## Genie Code transcript (summary)

> "Good — PRD loaded. Now let me inspect the samples.tpch schema to map PRD entities to actual
> tables. … Now let me record the gate result in the state file. … The seeded brief is at
> genie_brief.md and the gate is recorded in .vibecoding-state.md."

`docs/genie_brief.md` seeded from PRD + `samples.tpch`:
- **6 tables in scope:** orders, lineitem, customer, part, nation, region (supplier-side excluded)
- **11 candidate measures:** gross revenue, net revenue, AOV, order count, discount amount, return
  rate, etc.
- **15 sample questions** mapped from the PRD's three journeys (Revenue Analyst, Sales Ops, Finance)
- **9 semantic guardrails** — e.g. *"revenue" without qualification defaults to net revenue*
- **3 open questions** flagged for the user

Then it **stopped and asked the first clarifying question** (highest downstream impact):

> The PRD says "net revenue = gross minus refunds and discounts," but TPCH has no refund-amount
> column — only a return flag (`l_returnflag = 'R'`). Should net revenue be **(a)**
> `SUM(l_extendedprice * (1 - l_discount))` for all line items (discounts only — ignores returns),
> or **(b)** the same formula excluding returned items (`WHERE l_returnflag != 'R'`)?

## Artifact(s) produced

- `docs/genie_brief.md` (seeded, pending sign-off)
- `.vibecoding-state.md` gate result recorded

## Gate result

- [x] `design_prd.md` read; agent reused PRD journeys/entities instead of re-asking.
- [x] `genie_brief.md` seeded; interview triggered — but as a **one-at-a-time drip** (3 sequential
      questions), which was too much back-and-forth. See prompt edit below.
- [x] Gate result recorded in `.vibecoding-state.md`.
- [x] **Unprompted?** **YES** — GC surfaced the gross-vs-net / returns definitional conflict on its
      own. The Step 1 template names no conflict; it emerged from reading `l_discount` /
      `l_returnflag` against the PRD's loose "net revenue" wording.

## ⭐ Realism finding (flagged for spec fold-in)

**Conflict discovered during elicitation (Step 1), not at the Step 3 gate.** This is healthy: the
Step 3 gate then acts as a **confirmation / formalization** of a conflict already raised, not the
first surfacing. Consequence for the docs — Step 3's "Golden transcript should show" and the
runbook's unprompted-discovery acceptance check should accept the conflict **surfaced at Step 1 OR
Step 3**, rather than implying it must first appear at Step 3. (Step 1 prompt stays as-is — early
probing is desired.)

## Prompt edit applied (fold-in from this run)

**Finding:** "Elicit … one question at a time" made Genie Code drip 3 sequential questions (net-revenue
definition → supplier/margin scope → relative-time anchoring). Three round-trips was too much friction.

**Fix (applied to Step 1 template + design-spec §5 shape):** ask for **all** open questions in **one
batched, numbered list**, each pre-filled with a best-guess assumption marked "(assumed — correct
me)" so the operator only fixes what's wrong. Also reflected in the Step 1 "Golden transcript should
show" line. The three questions themselves were all reasonable/on-topic — the issue was cadence, not
content.

## Watch items for later steps

- 11 candidate measures is a lot → verify GC honors **"stop at five"** at Step 3.
- Answer given to the clarifying question (for continuity): net = `SUM(l_extendedprice*(1-l_discount))`
  (discounts only) as canonical; add separate **Returned Revenue** (`WHERE l_returnflag='R'`) and
  derived **Net Revenue after Returns**; keep **Gross** as documented alternate. All defs retained
  in the brief (the conflict is the finding, not a pick-one).
