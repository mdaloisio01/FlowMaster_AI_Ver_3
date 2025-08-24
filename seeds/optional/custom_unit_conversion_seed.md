# custom_unit_conversion_seed.md

## Purpose:
Ensure accurate, flexible, and context-aware unit conversions across all domains (tech, science, industry, informal).

---

## Core Conversions

### From => To Rules:
```yaml
standard_conversions:
  - from: PSI
    to: kPa
    formula: "x * 6.89476"
  - from: mm
    to: mesh
    formula: "lookup_table"
  - from: inHg
    to: ft_elevation
    formula: "x * 88.911"
  - from: °C
    to: °F
    formula: "(x * 9/5) + 32"
  - from: °C
    to: Kelvin
    formula: "x + 273.15"
```

### Default Output Units Per Context
```yaml
defaults:
  temperature: °C
  pressure: kPa
  length: cm
  currency: USD
```

---

## Add-ons & Future-Proofing

### Auto-Learning Conversion Memory
```yaml
auto_learning:
  enabled: true
  prompt_user_on_unknown_unit: true
  save_learned_units_to: /seeds/user_defined_units.yaml
```

---

### Conversion Confidence Ratings
```yaml
confidence_levels:
  standard_formula: 1.0
  user_defined: 0.75
  inferred: 0.5
```

---

### Time-Sensitive Conversions
```yaml
time_adjusted_units:
  currency:
    enabled: true
    source: "ECB API"
    cache_days: 3
  BTU_per_m3:
    adjust_by: "seasonal_region_factor"
```

---

### Bi-Directional Clarification Engine
```yaml
ambiguity_handler:
  ton:
    options: ["short_ton", "metric_ton", "long_ton"]
    ask_if_uncertain: true
```

---

### Slang & Alias Handling
```yaml
unit_aliases:
  shot: 44ml
  brick: 1kg
  scoop: 50g
  dash: 0.92ml
  pinch: 0.36g
```

---

### Localization Layer
```yaml
localization:
  enabled: true
  region_defaults:
    US: imperial
    EU: metric
    UK: mixed
```

---

### Visualization Templates
```yaml
visual_output:
  default_format: "bar_chart"
  enable_dual_axis: true
  render_engine: "matplotlib"
```

---

## Notes:
- All formulas are forward/backward compatible.
- Learned units can be exported per-client if needed.
- Unresolvable inputs trigger fallback clarification.

```
