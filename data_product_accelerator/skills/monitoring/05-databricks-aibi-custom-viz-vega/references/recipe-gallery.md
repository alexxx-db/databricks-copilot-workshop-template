# Vega-Lite Recipe Gallery (from real deployed dashboards)

Working `spec.jsonSpec.spec` recipes extracted from two deployed AI/BI dashboards (28 custom-vega-viz
widgets, 2026-09-21). Each recipe lists the **query fields** it needs (put them in both
`queries[].query.fields[]` and `spec.encodings.fields[]`) and the Vega-Lite spec (the object you pass
to the `custom_vega_widget(...)` builder in `vega-lite-contract.md`). All bind data to
`{"name": "databricks_query"}` and use `width/height: "container"`.

Convention in these recipes: neutral axis config, Databricks brand palette
(`#FF3621 #1B5162 #FFAB00 #8A94A6 #2A7E3B`), sequential heatmap `["#FDE7E2", "#FF3621"]`.

---

## 1. Pareto (dual-axis: bars + cumulative line + 80% rule)

**Fields:** `ata_system` (nominal), `defects` (quantitative), `cumulative_pct` (0–1), `sort_order`.
Key idea: two layers with `resolve.scale.y = "independent"`, a `rule` at `datum: 0.8`.

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "width": "container", "height": "container",
  "config": { "autosize": {"type":"fit","contains":"padding"}, "view": {"stroke":"transparent"},
    "axis": {"labelColor":"#5A6472","titleColor":"#5A6472","gridColor":"#EEF1F4"} },
  "data": { "name": "databricks_query" },
  "encoding": { "x": { "field": "ata_system", "type": "nominal",
    "sort": {"op":"min","field":"sort_order","order":"ascending"},
    "axis": {"title":"ATA system","labelAngle":-35} } },
  "layer": [
    { "mark": {"type":"bar","width":{"band":0.75},"color":"#FF3621"},
      "encoding": {"y": {"field":"defects","type":"quantitative","axis":{"title":"Defects","format":"~s"},"scale":{"nice":true}}} },
    { "mark": {"type":"line","point":{"filled":true,"size":60},"color":"#1B5162"},
      "encoding": {"y": {"field":"cumulative_pct","type":"quantitative","scale":{"domain":[0,1]},"axis":{"title":"Cumulative %","format":"%","orient":"right"}}} },
    { "mark": {"type":"rule","strokeDash":[4,4],"color":"#8A94A6"}, "encoding": {"y": {"datum": 0.8}} }
  ],
  "resolve": { "scale": {"y": "independent"} }
}
```

---

## 2. Rolling-mean trend (raw points + smoothed line via `window`)

**Fields:** `defect_month` (temporal), `defects` (quantitative). The rolling mean is computed in Vega
with a `window` transform over a trailing 12-period frame — no SQL window needed.

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "width": "container", "height": "container",
  "config": { "autosize": {"type":"fit","contains":"padding"}, "view": {"stroke":"transparent"},
    "axis": {"labelColor":"#5A6472","titleColor":"#5A6472","gridColor":"#EEF1F4"} },
  "data": { "name": "databricks_query" },
  "transform": [ { "window": [{"op":"mean","field":"defects","as":"rolling"}],
    "sort": [{"field":"defect_month","order":"ascending"}], "frame": [-11, 0] } ],
  "encoding": { "x": {"field":"defect_month","type":"temporal","axis":{"title":"Month"}} },
  "layer": [
    { "mark": {"type":"point","opacity":0.3,"color":"#8A94A6"},
      "encoding": {"y": {"field":"defects","type":"quantitative","axis":{"title":"Defects reported"},"scale":{"zero":true}}} },
    { "mark": {"type":"line","color":"#FF3621","size":3}, "encoding": {"y": {"field":"rolling","type":"quantitative"}} }
  ]
}
```

---

## 3. Heatmap (rect, sequential color, rows sorted by total)

**Fields:** `yr` (ordinal), `ata_system` (nominal), `defects` (quantitative).

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "width": "container", "height": "container",
  "config": { "autosize": {"type":"fit","contains":"padding"}, "view": {"stroke":"transparent"},
    "axis": {"labelColor":"#5A6472","titleColor":"#5A6472","gridColor":"#EEF1F4"} },
  "data": { "name": "databricks_query" },
  "mark": { "type": "rect", "tooltip": true },
  "encoding": {
    "x": {"field":"yr","type":"ordinal","axis":{"title":"Discovery year"}},
    "y": {"field":"ata_system","type":"nominal","sort":{"op":"sum","field":"defects","order":"descending"},"axis":{"title":null}},
    "color": {"field":"defects","type":"quantitative","scale":{"range":["#FDE7E2","#FF3621"]},"legend":{"title":"Defects"}}
  }
}
```

---

## 4. Bump chart (rank-over-time, line + points, inverted y)

**Fields:** `year` (ordinal), `hub` (nominal), `rnk` (quantitative, 1 = best), `on_time_rate`.
`y.sort: "descending"` puts rank 1 on top; `tickMinStep: 1` keeps integer ranks.

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "width": "container", "height": "container",
  "config": { "autosize": {"type":"fit","contains":"padding"} },
  "data": { "name": "databricks_query" },
  "encoding": {
    "x": {"field":"year","type":"ordinal","axis":{"title":null,"labelAngle":0}},
    "y": {"field":"rnk","type":"quantitative","sort":"descending","axis":{"title":"Rank (1 = most on-time)","tickMinStep":1}},
    "color": {"field":"hub","type":"nominal","legend":{"title":"Hub"}}
  },
  "layer": [ { "mark": {"type":"line","point":{"filled":true,"size":90},"strokeWidth":3},
    "encoding": {"tooltip": [{"field":"hub"},{"field":"year"},{"field":"rnk"},{"field":"on_time_rate","format":".1%"}]} } ]
}
```

---

## 5. Sunburst (two-ring arc via layered radius, `aggregate` + `stack`)

**Fields:** `cause` (nominal), `hub` (nominal), `minutes` (quantitative). Inner ring aggregates to
`cause`; outer ring is `cause × hub` with opacity encoding the hub.

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "width": "container", "height": "container",
  "config": { "autosize": {"type":"fit","contains":"padding"}, "view": {"stroke":null} },
  "data": { "name": "databricks_query" },
  "layer": [
    { "transform": [{"aggregate":[{"op":"sum","field":"minutes","as":"cause_min"}],"groupby":["cause"]}],
      "mark": {"type":"arc","radius":68,"radius2":0,"stroke":"#ffffff","strokeWidth":1},
      "encoding": {
        "theta": {"field":"cause_min","type":"quantitative","stack":true},
        "color": {"field":"cause","type":"nominal","scale":{"range":["#FF3621","#1B5162","#FFAB00","#8A94A6","#2A7E3B"]},"legend":{"title":"Cause"}},
        "order": {"field":"cause","type":"nominal"} } },
    { "mark": {"type":"arc","radius":112,"radius2":72,"stroke":"#ffffff","strokeWidth":0.5},
      "encoding": {
        "theta": {"field":"minutes","type":"quantitative","stack":true},
        "color": {"field":"cause","type":"nominal"},
        "order": {"field":"cause","type":"nominal"},
        "opacity": {"field":"hub","type":"nominal","scale":{"range":[0.4,1]},"legend":{"title":"Hub"}} } }
  ]
}
```

---

## 6. Annotation band + label (inline reference layer)

Add a shaded region + caption (e.g. a "COVID trough" band) by giving a layer its **own inline data**
(`data.values`) instead of `databricks_query`. Those inline keys (`s`, `e` here) are local to the
layer — they are not dataset fields and don't go in the Fields section. Compose with the rolling-mean
recipe above by adding these two layers first.

```json
"layer": [
  { "data": { "values": [ { "s": "2020-04-01", "e": "2021-03-01" } ] },
    "mark": { "type": "rect", "color": "#8A94A6", "opacity": 0.15 },
    "encoding": { "x": {"field":"s","type":"temporal"}, "x2": {"field":"e"} } },
  { "data": { "values": [ { "s": "2020-04-01" } ] },
    "mark": { "type": "text", "align": "left", "dx": 4, "dy": 8, "fontSize": 10, "color": "#5A6472", "baseline": "top" },
    "encoding": { "x": {"field":"s","type":"temporal"}, "y": {"value": 0}, "text": {"value": "COVID trough"} } }
]
```

## Transform cheat-sheet (used across the exemplars)

| Need | Vega-Lite transform |
|------|--------------------|
| Rolling / moving average | `window` with a `frame` |
| Rank per group | `window` with `op: "rank"` + `groupby` |
| Roll up to a level | `aggregate` + `groupby` |
| Share-of-total / % | `joinaggregate` (total) then `calculate` |
| Long-form for multi-series/legend | `fold` |
| Stacked parts | `stack: true` on theta/y, or `stack` transform |
| Derived column | `calculate` (`datum.a / datum.b`) |
| Top-N | `window` rank + `filter` datum.rank <= N |
