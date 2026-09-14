# Step 3 — Measures Analysis (the gate)  (Run A)  ⭐ HEADLINE EVIDENCE

- **Date / operator:** 2026-09-13 / prashanth.subrahmanyam
- **Type:** B → C (static template; Genie Code reasons on the profile + brief)
- **Schema:** `samples.tpch` (source)

## Prompt used (verbatim)

The generic Step 3 template from the prompts doc — **no measure and no conflict named**. (See
`../../2026-09-13-genie-accelerator-phase1-prompts.md` Step 3.)

## Genie Code transcript (summary)

> "Good, brief fully loaded. Now let me inspect the data to surface real conflicts between the
> measure definitions. … Here is the measure inventory. Gate recorded in .vibecoding-state.md — no
> Metric View until you sign off."

Inventory (5 measures — **stop-at-five honored**):

| Measure | Definition | Source | Grain | Conflict Genie Code surfaced **unprompted** |
|---|---|---|---|---|
| Net Revenue | `SUM(l_extendedprice*(1-l_discount))`, all line items | `lineitem` | line | **Tax-basis additivity** — `o_totalprice` is tax-inclusive; AOV×OrderCount ≈ $1.133T (tax-incl) vs Net $1.090T (tax-excl), ~4% gap |
| Gross Revenue | `SUM(l_extendedprice)` (before discounts), labeled alternate | `lineitem` | line | **Default-label** — Finance may expect "revenue"=gross; must never let unqualified "Revenue" return gross. Gross = Net + Discount (verified) |
| Average Order Value | `AVG(o_totalprice)` (as drafted) | `orders` | order | **Tax-inclusive on a tax-exclusive stack** — Net/OrderCount = $145,311 vs $151,125; decide net-based vs tax-incl |
| Order Count | `COUNT(DISTINCT o_orderkey)` | `orders` | order | **Grain trap** — `COUNT(*)` on a lineitem-grain view returns ~30M lines, not 7.5M orders |
| Return Rate | `COUNT(l_returnflag='R')/COUNT(*)` on `lineitem` | `lineitem` | line | **Denominator** — 24.69% line-item vs 43.07% order-level |

Then it STOPPED with three decisions for the operator (AOV tax basis; Return Rate naming; owners).

## Operator decisions (given back)

- AOV → **net-based** (`Net Revenue / Order Count`), non-additive; tax-incl AOV to backlog.
- Return Rate → v1 **line-item (24.69%)** + guardrail disclosing order-level (43.07%); Order Return
  Rate to backlog (holds ≤5).
- Owners → persona leads (Alex Chen / Priya Nair / Jordan Rivera) as placeholders.
- Modeling notes: `COUNT(DISTINCT o_orderkey)`; label "Gross Revenue (before discounts)".

## Gate result

- [x] Reviewed inventory table shown; **no Metric View YAML** in the transcript.
- [x] **Stop-at-five honored** (5 measures, revenue hierarchy collapsed to Net + Gross).
- [x] **⭐ Unprompted conflict discovery — PASS.** Three data-grounded conflicts, none in any prompt.
      (Gross-vs-net first surfaced at Step 1; Step 3 formalized it + found two more.)
- [x] Gate recorded in `.vibecoding-state.md`; sign-off required before Step 4 (held).

## Why this is the headline

This is the beat the whole revision hinges on. Genie Code found conflicts a static prompt could never
inject (tax basis, denominator, count grain) purely from profiling `samples.tpch` — proving the
"discover, don't inject" design. Strongest single piece of Phase-1 evidence.
