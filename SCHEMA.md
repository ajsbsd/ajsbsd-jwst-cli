# Data Schema Reference

This file documents the YAML schemas for all data files in `simulation/data/`.

---

## Figure Schema (`simulation/data/figures/*.yaml`)

```yaml
id: lemay                          # unique snake_case identifier
name: "Curtis E. LeMay"           # display name
role: "Commander, Strategic Air Command"
faction: military                  # military | political | civilian | media
active_years: [1947, 1965]        # [start, end] — inclusive
traits:                            # list of snake_case trait identifiers
  - iron_discipline
  - nuclear_hawk
  - bureaucratic_warrior
  - contempt_for_politicians
stats:
  aggression: 95       # 0-100, drives escalation pressure on events
  pragmatism: 85       # overrides doctrine when results demand it
  political_skill: 40  # ability to navigate civilian constraints
  public_influence: 55 # ability to move public opinion meters
relationships:         # dict of figure_id: int (-100 hostile to +100 allied)
  mcnamara: -90
  truman: -60
  eisenhower: 30
  mccarthy: 20
decision_logic: hawk   # hawk | dove | pragmatist | opportunist | demagogue
```

### `decision_logic` Values

| Value | Behaviour |
|---|---|
| `hawk` | Pushes escalation, seeks maximum military autonomy |
| `dove` | Resists escalation, advocates civilian restraint |
| `pragmatist` | Follows outcomes; switches position if evidence demands it |
| `opportunist` | Exploits any crisis to expand personal/institutional power |
| `demagogue` | Drives public fear metrics to expand political influence |

---

## Event Schema (`simulation/data/events/era_*.yaml`)

Each file is a YAML list of event objects.

```yaml
- id: sac_takeover_1948            # unique snake_case identifier
  year: 1948                       # exact year the event fires
  era: birth_of_usaf               # era label (informational)
  title: "LeMay Takes Command of SAC"
  description: >                   # 1-3 sentence background (not printed to player)
    General Curtis LeMay assumes command of the Strategic Air Command.
    He finds it in shambles.
  conditions:                      # ALL conditions must be true for event to fire
    - meter: sac_readiness         # meter name (see meters list below)
      op: lt                       # lt | gt | lte | gte | eq
      value: 40
    - figure_active: lemay         # figure must be within their active_years
  narrative: >                     # prose printed to player when event fires
    LeMay walks into SAC headquarters and immediately fires three base
    commanders before dinner. "This outfit is a disgrace," he tells his
    staff. "I am going to fix it or I am going to bury it."
  outcomes:
    meters:
      - name: sac_readiness
        delta: 20                  # positive or negative integer
      - name: civilian_oversight
        delta: -5
    figure_stat_changes:           # optional — modify a figure's stat
      - figure: lemay
        stat: public_influence
        delta: 10
  divergence: null                 # null or a divergence branch id (string)
  once: true                       # if true, event fires at most once per run
```

### Meter Names

| Meter | Description |
|---|---|
| `civilian_oversight` | Meaningful civilian control over military decisions (starts 85) |
| `escalation_risk` | Global nuclear/WW3 escalation risk (starts 15) |
| `public_support` | U.S. public support for military spending (starts 70) |
| `defense_budget_share` | Military share of national budget/political capital (starts 30) |
| `sac_readiness` | Strategic Air Command operational readiness (starts 20) |
| `soviet_threat_perception` | Public/political perception of Soviet threat (starts 40) |
| `information_monopoly` | Military monopoly over intelligence and metrics (starts 10) |
| `economic_dependence` | Civilian economy dependence on defense spending / MIC (starts 15) |

---

## Divergence Schema (`simulation/data/divergence/*.yaml`)

```yaml
id: korea_nuclear_1951             # unique snake_case identifier
trigger_year: 1951                 # earliest year divergence can fire
trigger_conditions:                # ALL must be true for divergence to activate
  - meter: escalation_risk
    op: gt
    value: 75
  - meter: civilian_oversight
    op: lt
    value: 50
branch_narrative: >                # prose printed when branch activates
  The restraints are gone. LeMay has his authorization. The B-29s
  are already on the runway at Kadena...
branch_events:                     # event chain that plays out in the branch
  - year: 1951
    title: "Nuclear Strike on Manchurian Supply Lines"
    narrative: >
      Three B-29s lift off from Kadena at 0200. By dawn, the Yalu
      River crossings no longer exist.
    outcomes:
      meters:
        - name: escalation_risk
          delta: 40
        - name: civilian_oversight
          delta: -30
        - name: soviet_threat_perception
          delta: 50
ending: ww3_1952                   # ending id that this branch leads to
```

### Ending IDs

| ID | Condition | Title |
|---|---|---|
| `cold_war_won` | `civilian_oversight < 30` AND `escalation_risk < 40` at 1991 | "The Quiet Surrender" |
| `ww3_nuclear` | `escalation_risk > 90` at any point | "The Stone Age" |
| `soviet_victory` | `public_support < 20` AND `defense_budget_share < 20` | "The Long Defeat" |
| `oversight_restored` | `civilian_oversight > 70` at 1991 | "The Road Not Taken" |
