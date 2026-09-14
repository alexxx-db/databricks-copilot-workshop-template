# Analytical patterns cookbook (Metric View YAML)

Advanced, reusable measure/dimension patterns for Unity Catalog Metric Views, distilled from the
official **[databricks-solutions/uc-semantics-patterns](https://github.com/databricks-solutions/uc-semantics-patterns)**
reference library (Databricks License). Each pattern there ships a scenario, the YAML, and a **verified
test query + expected output** on the standard **TPC-H / TPC-DS** sample datasets — so numbers are
reproducible in any workspace. Use this file for the *distilled* pattern; go to the source repo when you
need the exact verified output or a fuller worked example.

**How to use:** these are `version: "1.1"` patterns. For the base window-measure mechanics (`window:`,
`order`, `range`, `semiadditive`, `offset`) see `composability-patterns.md`; for LOD see
`level-of-detail.md`. This file covers the four families NOT already in those references, plus a
workshop-fit note.

> **Sample-data fit (important):** Ranking and Static Segmentation run directly on **`samples.tpch`**
> (orders + customer + nation + region). Semi-additive needs an inventory/balance table with a
> prior-period column, and Currency conversion needs an FX-rate table — neither exists in plain TPC-H,
> so treat those two as **BYO-data / synthetic-only** patterns.

---

## 1. Ranking (dynamic vs static, global vs partitioned)

**Scenario:** leaderboards — rank customers/regions by a measure, either globally or reset per year.
**Source:** `Ranking/` (TPC-H `orders` → `customer` → `nation` → `region`). Fits `samples.tpch`.

The rank is expressed **as a measure** using a SQL window function over an aggregate. Swap the window
function for the ranking semantics you want:

| Function | Semantics |
|---|---|
| `RANK()` | Leaderboard position; **gaps** after ties (1,2,2,4) |
| `DENSE_RANK()` | Tiers; **no gaps** after ties (1,2,2,3) |
| `ROW_NUMBER()` | Unique position per row (#1,#2,#3) |
| `NTILE(n)` | Split into n buckets (halves, quartiles) |
| `PERCENT_RANK()` | Relative standing 0–1 |
| `CUME_DIST()` | Share of rows at or below this rank |

```yaml
version: "1.1"
source: orders
measures:
  - name: OrderCount
    display_name: Order Count
    expr: COUNT(o_orderkey)

  # Dynamic rank — recomputes as the user filters / regroups
  - name: DynamicRankByOrders
    display_name: Dynamic Rank by Orders
    expr: RANK() OVER (ORDER BY COUNT(o_orderkey) DESC)

  # Partitioned — rank resets within each year
  - name: RankByOrdersPerYear
    display_name: Rank by Orders (per Year)
    expr: RANK() OVER (PARTITION BY `Year` ORDER BY COUNT(o_orderkey) DESC)

  # Buckets / percentile
  - name: OrdersQuartile
    expr: NTILE(4) OVER (ORDER BY COUNT(o_orderkey) DESC)
  - name: OrdersPercentRank
    expr: PERCENT_RANK() OVER (ORDER BY COUNT(o_orderkey) DESC)
    format: { type: number, decimal_places: { type: exact, places: 2 } }
```

**Dynamic vs static:** the measures above are **dynamic** — they re-rank whenever the query's
filters/grouping change. For a **static** rank that is fixed regardless of how the user later regroups,
bake the aggregate into a **dimension** with its own `OVER (…)` and rank off that field:

```yaml
fields:
  - name: OrderCount_dim
    expr: COUNT(o_orderkey) OVER (PARTITION BY `Year`)
measures:
  - name: StaticRankByOrders
    expr: RANK() OVER (ORDER BY `OrderCount_dim` DESC)
```

**Genie/workshop use:** great "stretch" measures for a revenue Genie Agent — "top 10 customers by
orders", "rank regions this year". Add 2–3, not all six.

---

## 2. Semi-additive balances (opening / closing / growth)

**Scenario:** stock levels, account/inventory balances — measures you **cannot SUM across time** (you
sum across products at a point in time, but take first/last down the time axis).
**Source:** `Semi-additive calculations/` (TPC-DS `inventory_daily` + `date_dim`/`item`/`warehouse`).
**Needs:** a daily-balance table with a **prior-period** column (`inv_quantity_on_hand_prev_day`) —
**not in plain TPC-H**; BYO/synthetic only.

The mechanism is a `window` with `range: current` + `semiadditive: first|last`:

```yaml
version: "1.1"
source: inventory_daily
measures:
  - name: _Quantity
    expr: SUM(inv_quantity_on_hand)
  - name: _QuantityPrevDay
    expr: SUM(inv_quantity_on_hand_prev_day)

  - name: OpeningBalance
    display_name: Opening Balance
    expr: _QuantityPrevDay
    window:
      - order: Date
        range: current
        semiadditive: first
  - name: ClosingBalance
    display_name: Closing Balance
    expr: _Quantity
    window:
      - order: Date
        range: current
        semiadditive: last

  - name: GrowthInPeriod
    display_name: Growth in Period
    expr: COALESCE(AGG(ClosingBalance), 0) - COALESCE(AGG(OpeningBalance), 0)
```

**Key idea:** `semiadditive: first|last` picks the first/last value along `order` when the time
dimension isn't in the GROUP BY, so the balance stays correct at every rollup grain. Reference sibling
measures inside another measure with `AGG(<measure>)`.

---

## 3. Currency conversion (query-time parameter + FX join)

**Scenario:** let the user pick a reporting currency at query time and convert on the fly using
historical monthly rates.
**Source:** `Currency conversion/` (TPC-H `orders` + an `exchange_rate` table). **Needs:** an FX table
(`from_currency`, `to_currency`, `rate_type`, `rate_month`, `rate`) — BYO/synthetic only.

This is the **parameterized Metric View** pattern — a `parameters:` block whose value is used inside a
join `on`:

```yaml
version: "1.1"
source: orders
parameters:
  - name: p_target_currency
    data_type: STRING
    default: "'EUR'"
joins:
  - name: fx
    source: exchange_rate
    'on': |-
      fx.rate_month = DATE_TRUNC('month', source.o_orderdate)
      AND fx.from_currency = 'USD'
      AND fx.to_currency = p_target_currency
      AND fx.rate_type = 'AVG'
    rely: { at_most_one_match: true }
measures:
  - name: TotalPriceUSD
    display_name: Total Price (USD)
    expr: SUM(o_totalprice)
    format: { type: currency, currency_code: USD }
  - name: TotalPriceConverted
    display_name: Total Price (converted)
    expr: SUM(o_totalprice * fx.rate)
```

**Why it matters for Genie:** the parameter lets a single governed measure answer "…in EUR / GBP / JPY"
without a measure per currency. The repo also has multi-source-currency and multiple-rate-type variants.

---

## 4. Static segmentation (price bands, per-category bands, config table)

**Scenario:** bucket rows into named bands (Low/Medium/High) for slicing — globally, or with thresholds
that vary by category.
**Source:** `Static segmentation/` (TPC-H `orders` + `customer`). Fits `samples.tpch`.

Segments are **CASE-based dimensions**. Add a parallel `*Sort` dimension so bands order correctly in a
BI/Genie result instead of alphabetically:

```yaml
version: "1.1"
source: orders
fields:
  # Global price bands (Min <= value < Max)
  - name: PriceSegment
    display_name: Price Segment
    expr: >
      CASE
        WHEN o_totalprice < 50000 THEN 'VERY LOW'
        WHEN o_totalprice < 150000 THEN 'LOW'
        WHEN o_totalprice < 300000 THEN 'MEDIUM'
        ELSE 'HIGH'
      END
  - name: PriceSegmentSort
    display_name: Price Segment Sort
    expr: >
      CASE
        WHEN o_totalprice < 50000 THEN 1
        WHEN o_totalprice < 150000 THEN 2
        WHEN o_totalprice < 300000 THEN 3
        ELSE 4
      END

  # Per-category bands — thresholds differ by segment
  - name: CategoryPriceSegment
    expr: >
      CASE customer.c_mktsegment
        WHEN 'AUTOMOBILE' THEN
          CASE WHEN o_totalprice < 100000 THEN 'LOW'
               WHEN o_totalprice < 300000 THEN 'MEDIUM' ELSE 'HIGH' END
        ELSE
          CASE WHEN o_totalprice < 50000 THEN 'LOW'
               WHEN o_totalprice < 150000 THEN 'MEDIUM' ELSE 'HIGH' END
      END
```

**Config-table variant:** for thresholds you want to change without editing YAML, the repo's
`Static_segmentation_config.*` files join a small **band config table** instead of hard-coding the CASE
bounds — better for governance and business self-service. Use that when bands change often.

---

## Attribution

Patterns distilled from **[databricks-solutions/uc-semantics-patterns](https://github.com/databricks-solutions/uc-semantics-patterns)**
(© Databricks, Inc., Databricks License). YAML here is condensed/reformatted; see the source folders
(`Ranking/`, `Semi-additive calculations/`, `Currency conversion/`, `Static segmentation/`,
`Time Intelligence/`) for full definitions, verified test queries, and expected TPC-H/TPC-DS outputs.
Databricks support does not cover that repo; file issues there for pattern bugs.
