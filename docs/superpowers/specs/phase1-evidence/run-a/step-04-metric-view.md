# Step 4 — Draft the Metric View  (Run A)

- **Date / operator:** 2026-09-13 / prashanth.subrahmanyam
- **Type:** B (static template)
- **Source:** `samples.tpch` (read-only) · **Write target:** `serverless_stable_6t92c3_catalog.revenuescope`
- **MV:** `order_revenue_metrics`

## Prompt used (verbatim)

Step 4 Path B template (draft → review → create), with the source/write split. (See prompts doc Step 4.)

## Genie Code transcript (summary)

Two builds occurred:
1. **Prior session (nested joins):** created `order_revenue_metrics` with **4-level snowflake joins**
   (`lineitem → orders → customer → nation → region`, plus `lineitem → part`). All dimensions
   resolved; all 5 measures returned correct values; region×year slice validated.
2. **This session (pre-joined rebuild):** the Step 4 prompt asked to prefer a pre-joined source; GC
   detected the existing view and proposed `CREATE OR REPLACE` with a **pre-joined SQL-subquery
   source** (all exprs reference `source.*` at one level). Proposed plan + YAML shown for review.

## Validated aggregates (global)

| Measure | Value | Check |
|---|---|---|
| Net Revenue | 1,089,835,179,247 | tax-exclusive, canonical (matches Layer-2 1.090T) |
| Gross Revenue | 1,147,191,013,439 | before discounts; Gross = Net + Discount (identity holds) |
| Average Order Value | 145,311 | **net-based**, not tax-incl 151,125 (operator decision honored) |
| Order Count | 7,500,000 | `COUNT(DISTINCT)`, not `COUNT(*)` (grain trap avoided) |
| Return Rate | 24.69% | line-item basis (operator decision honored) |

YAML v1.1 with `display_name`, `synonyms`, and `format` on every field/measure. AOV flagged
non-additive. Dimension slicing (region × year) validated.

## ⭐ Findings folded into the spec/prompts

1. **Nested snowflake joins WORK** — the Layer-2 "gotcha" (finicky nested dimension refs) was a
   hand-authored CLI syntax issue, **not** a platform limit. Corrected the Step 4 note; pre-joined
   source is now framed as *recommended*, not *required*.
2. **Parity:** pre-joined-subquery rebuild is expected to return **identical** numbers to the
   nested-join version — the requested parity re-run confirms the refactor is safe (regression check).
3. **Source vs write target:** `samples.tpch` read-only forced a separate writable schema; GC had to
   guess one → added `{write_catalog}.{write_schema}` variable to Conventions + Steps 4/7/11.
4. **Idempotency:** GC correctly detected the pre-existing MV and proposed `CREATE OR REPLACE` →
   codified "use CREATE OR REPLACE and check state/target first" into the Step 4 create prompt.
5. **Synonyms added here already** → Step 5 reframed as review/expand.

## Gate result

- [x] Each approved measure → 1 Metric View; `MEASURE()` returns; non-additive (AOV) flagged.
- [x] YAML reviewed before creation; business-friendly display names.
- [ ] Pre-joined rebuild parity re-run — **pending operator confirmation** (numbers must match table above).
