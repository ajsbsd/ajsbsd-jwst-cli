# Cold War Simulation — Plan

## Top-Level Overview

**Goal:** Build a Python data-driven narrative engine simulating the Cold War (1947–1991), tracking the erosion of civilian oversight of the U.S. military. Historical figures (LeMay, McNamara, McCarthy, etc.) run on rules-based logic. The simulation follows real history by default but branches at key divergence points (e.g., nuclear use in Korea). The player observes: narrative prose as events unfold, plus periodic state summaries showing global meters.

**Core Thesis Being Demonstrated:** Civilian control of the U.S. military was permanently and irreversibly eroded between 1947 and 1991 through four mechanisms — technological dependence, information monopoly, economic hostage-taking (MIC), and the Crisis Ratchet.

**Approach:** Modular Python package. Data is separated from engine logic. Figures, events, and eras are defined in YAML data files. The engine processes turns (each turn = ~1 year), evaluates conditions, triggers events, updates meters, and prints narrative output.

---

## Architecture Overview

```
simulation/
  engine.py          # Main loop, turn processing, meter updates
  figures.py         # Figure class — stats, relationships, decision logic
  events.py          # Event loader, condition evaluator, outcome applicator
  meters.py          # Global state meters
  narrative.py       # Prose output and state summary printer
  data/
    figures/         # YAML files per figure (LeMay, McNamara, McCarthy, etc.)
    events/          # YAML files per era (1947-1953, 1953-1961, etc.)
    divergence/      # YAML files for alternate timeline branches
  main.py            # Entry point
```

---

## Sub-Tasks

---

### Sub-Task 1 — Project Scaffold and Package Structure

**Intent:** Establish the Python package layout, entry point, and dependencies so all subsequent sub-tasks have a stable foundation to build on.

**Expected Outcomes:**
- `simulation/` package exists with `__init__.py` files
- `main.py` entry point runs without error (prints a startup banner and exits cleanly)
- `requirements.txt` lists all dependencies (PyYAML, rich for terminal output)
- `README.md` describes what the project is and how to run it

**Todo List:**
1. Create `simulation/` directory with `__init__.py`
2. Create subdirectories: `simulation/data/figures/`, `simulation/data/events/`, `simulation/data/divergence/`
3. Create stub modules: `engine.py`, `figures.py`, `events.py`, `meters.py`, `narrative.py`
4. Create `main.py` that imports the engine and prints a startup banner
5. Create `requirements.txt` with `pyyaml` and `rich`
6. Create `README.md` with project description and run instructions

**Relevant Context:** Greenfield project. No existing code. The `rich` library provides styled terminal output for the narrative prose and meter display panels.

**Status:** `[ ] pending`

---

### Sub-Task 2 — Global Meters System

**Intent:** Define and implement the core global state meters that track the simulation's thesis. Every event outcome modifies these meters. They are the quantified backbone of the narrative.

**Expected Outcomes:**
- `meters.py` contains a `GlobalMeters` dataclass with all defined meters
- Meters can be updated by name with `+/-` delta values
- Meters are clamped to `[0, 100]`
- A `summary()` method returns a formatted state summary for the narrative printer

**Meters to Implement:**

| Meter | Description | Start Value |
|---|---|---|
| `civilian_oversight` | How much meaningful civilian control exists over military decisions | 85 |
| `escalation_risk` | Global risk of nuclear/WW3 escalation | 15 |
| `public_support` | U.S. public support for the military and its spending | 70 |
| `defense_budget_share` | Military's share of national budget/political capital | 30 |
| `sac_readiness` | Strategic Air Command operational readiness | 20 |
| `soviet_threat_perception` | U.S. public/political perception of Soviet threat level | 40 |
| `information_monopoly` | Military's monopoly over intelligence/metrics vs. civilian access | 10 |
| `economic_dependence` | How dependent the civilian economy is on defense spending (MIC) | 15 |

**Todo List:**
1. Define `GlobalMeters` dataclass in `meters.py`
2. Implement `update(name, delta)` method with clamping
3. Implement `summary()` method that returns a dict of current values
4. Write a simple unit test in `tests/test_meters.py` to verify clamping and update logic

**Relevant Context:** The four erosion mechanisms map directly to meters: technological dependence -> `sac_readiness`/`defense_budget_share`; information monopoly -> `information_monopoly`; economic hostage -> `economic_dependence`; Crisis Ratchet -> `escalation_risk` feeding back into `civilian_oversight` loss.

**Status:** `[ ] pending`

---

### Sub-Task 3 — Figure Data Model and YAML Schema

**Intent:** Define the schema for historical figures and implement the `Figure` class. Figures have stats, relationships to other figures, a decision-making logic type, and a set of traits that modulate their behavior.

**Expected Outcomes:**
- `figures.py` contains a `Figure` dataclass loaded from YAML
- `simulation/data/figures/` contains YAML files for the first cohort of figures
- Each figure has: `id`, `name`, `role`, `faction`, `stats`, `traits`, `relationships`, `active_years`
- A `FigureRegistry` class loads all figures from the data directory

**Figures for Initial Data (YAML files):**
- `lemay.yaml` — General Curtis LeMay
- `mcnamara.yaml` — Robert McNamara
- `mccarthy.yaml` — Senator Joseph McCarthy
- `truman.yaml` — President Truman
- `eisenhower.yaml` — President Eisenhower
- `johnson.yaml` — President Lyndon B. Johnson
- `reagan.yaml` — President Ronald Reagan

**Figure YAML Schema:**
```yaml
id: lemay
name: "Curtis E. LeMay"
role: "Commander, Strategic Air Command"
faction: military  # military | political | civilian | media
active_years: [1947, 1965]
traits:
  - iron_discipline
  - nuclear_hawk
  - bureaucratic_warrior
  - contempt_for_politicians
stats:
  aggression: 95       # 0-100, drives escalation pressure
  pragmatism: 85       # overrides doctrine when results matter
  political_skill: 40  # ability to navigate civilian constraints
  public_influence: 55 # ability to move public opinion
relationships:
  mcnamara: -90        # hostile
  truman: -60
  eisenhower: 30
  mccarthy: 20         # shared anti-communism, contempt for methods
decision_logic: hawk   # hawk | dove | pragmatist | opportunist | demagogue
```

**Todo List:**
1. Define the YAML schema (document it in a `SCHEMA.md` file)
2. Implement `Figure` dataclass in `figures.py`
3. Implement `FigureRegistry` with a `load_all(data_dir)` class method
4. Write the six initial YAML figure files
5. Write a unit test that loads all figures and verifies required fields

**Relevant Context:** `decision_logic` is the key field used by the engine to determine how a figure responds to events. Hawks push for escalation and increased defense autonomy. Pragmatists weigh outcomes. Opportunists exploit crises for power.

**Status:** `[ ] pending`

---

### Sub-Task 4 — Event Data Model and YAML Schema

**Intent:** Define the schema for historical events and the condition/outcome evaluation system. Events are the core driver of the simulation — they fire when their conditions are met, apply outcomes to meters and figures, and emit narrative text.

**Expected Outcomes:**
- `events.py` contains `Event` dataclass and `EventEngine` class
- `simulation/data/events/` contains YAML event files organized by era
- Conditions reference meter thresholds and active figures
- Outcomes specify meter deltas and narrative text
- Divergence points are flagged and link to alternate branch files

**Event YAML Schema:**
```yaml
id: sac_takeover_1948
year: 1948
era: birth_of_usaf
title: "LeMay Takes Command of SAC"
description: >
  General Curtis LeMay assumes command of the Strategic Air Command.
  He finds it in shambles — broken planes, low morale, poor readiness.
  He immediately begins transforming it into the world's most lethal
  nuclear strike force.
conditions:
  - meter: sac_readiness
    op: lt
    value: 40
  - figure_active: lemay
narrative: >
  LeMay walks into SAC headquarters and immediately fires three base
  commanders before dinner. "This outfit is a disgrace," he tells his
  staff. "I am going to fix it or I am going to bury it."
outcomes:
  meters:
    - name: sac_readiness
      delta: +20
    - name: civilian_oversight
      delta: -5
    - name: defense_budget_share
      delta: +8
  figure_stat_changes:
    - figure: lemay
      stat: public_influence
      delta: +10
divergence: null  # or a reference to a divergence YAML file
```

**Event Era Files:**
- `era_1947_1953.yaml` — Birth of USAF, Berlin Airlift, SAC buildout, Korea
- `era_1953_1961.yaml` — McCarthy hearings, Eisenhower/MIC warning, bomber gap
- `era_1961_1968.yaml` — McNamara, Flexible Response, Cuban Missile Crisis, Vietnam/Rolling Thunder
- `era_1968_1980.yaml` — Nixon, detente, Watergate, SALT
- `era_1980_1991.yaml` — Reagan buildup, SDI, Gorbachev, Cold War end

**Todo List:**
1. Define the event YAML schema (add to `SCHEMA.md`)
2. Implement `Event` dataclass in `events.py`
3. Implement condition evaluator (`evaluate_conditions(event, meters, figures)`)
4. Implement outcome applicator (`apply_outcomes(event, meters, figures)`)
5. Implement `EventEngine` with `load_era(era_file)` and `get_eligible_events(year, meters, figures)`
6. Write a minimum of 5 events per era (25+ events total) in YAML files
7. Write unit tests for condition evaluation and outcome application

**Relevant Context:** Events must be designed so that historically, the default path always fires. Divergence events only fire when meters are in non-historical ranges (e.g., `escalation_risk > 80` in 1951 triggers the nuclear Korea branch).

**Status:** `[ ] pending`

---

### Sub-Task 5 — Divergence System (Alternate Timelines)

**Intent:** Implement the branching logic that detects when the simulation has diverged from historical conditions and transitions into an alternate timeline narrative. This is how the simulation demonstrates what LeMay wanted to do vs. what actually happened.

**Expected Outcomes:**
- `simulation/data/divergence/` contains YAML files for each alternate branch
- The engine detects divergence conditions at key historical junctures
- When a divergence fires, the narrative clearly marks the branch point
- Divergence timelines have their own event chains that lead to distinct endings

**Key Divergence Points:**
1. **Korea 1951 — Nuclear Authorization:** If `escalation_risk > 75` and `civilian_oversight < 50` when the Korea events fire, LeMay gets nuclear authorization. Branch leads to China entering the war, then Soviet response, then WW3 or ceasefire.
2. **1962 — Cuban Missile Crisis:** If `escalation_risk > 70`, LeMay's recommendation for airstrikes is followed. Branch leads to Soviet tactical nuclear response in Cuba or Berlin.
3. **Vietnam 1965 — LeMay's Unrestricted Bombing:** If `civilian_oversight < 40` and `information_monopoly > 60`, McNamara's target restrictions are bypassed. Branch leads to rapid North Vietnamese collapse but Chinese intervention.

**Divergence YAML Schema:**
```yaml
id: korea_nuclear_1951
trigger_year: 1951
trigger_conditions:
  - meter: escalation_risk
    op: gt
    value: 75
  - meter: civilian_oversight
    op: lt
    value: 50
branch_narrative: >
  The restraints are gone. LeMay has his authorization. The B-29s
  are already on the runway at Kadena, their bomb bays loaded with
  weapons that will rewrite the map of Asia...
branch_events:
  - year: 1951
    title: "Nuclear Strike on Manchurian Supply Lines"
    outcomes:
      meters:
        - name: escalation_risk
          delta: +40
        - name: civilian_oversight
          delta: -30
        - name: soviet_threat_perception
          delta: +50
ending: ww3_1952
```

**Todo List:**
1. Define divergence YAML schema (add to `SCHEMA.md`)
2. Write the three key divergence branch files
3. Implement divergence detection in the engine's turn loop
4. Implement branch transition logic (saves branch state, switches event queue)
5. Implement ending conditions and ending narrative display

**Relevant Context:** Divergence detection runs after normal event processing each turn. The engine checks all loaded divergence files and fires the first one whose conditions are met. Once a divergence fires, the simulation is flagged as `branched = True` and subsequent events are drawn from the branch file.

**Status:** `[ ] pending`

---

### Sub-Task 6 — Engine Turn Loop

**Intent:** Implement the core simulation engine that drives the year-by-year turn loop — advancing time, evaluating events, updating figures, checking divergence, and handing output to the narrative printer.

**Expected Outcomes:**
- `engine.py` contains `SimulationEngine` class
- `run()` method advances turns from `START_YEAR=1947` to `END_YEAR=1991`
- Each turn: loads eligible events -> fires applicable events -> applies outcomes -> checks divergence -> prints narrative + state summary
- Engine is configurable with a random seed for reproducibility

**Turn Loop Pseudocode:**
```
for year in range(1947, 1992):
    eligible = event_engine.get_eligible_events(year, meters, figures)
    for event in eligible:
        narrative.print_event(event)
        event_engine.apply_outcomes(event, meters, figures)
    divergence = divergence_engine.check(year, meters, figures)
    if divergence:
        narrative.print_divergence(divergence)
        event_engine.switch_to_branch(divergence)
    if year % 4 == 0:  # every 4 years, print full state summary
        narrative.print_summary(year, meters, figures)
```

**Todo List:**
1. Implement `SimulationEngine.__init__` — wire together meters, figure registry, event engine, divergence engine, narrative printer
2. Implement `run()` turn loop per pseudocode
3. Add `--seed` CLI argument via `argparse` in `main.py`
4. Add `--verbose` flag that prints state summary every year instead of every 4
5. Write an integration test that runs the engine for 5 turns and asserts expected meter ranges

**Relevant Context:** The engine does not make decisions — it only evaluates conditions and applies outcomes. All decision-making logic lives in the event YAML files and the figure `decision_logic` field. The engine is a pure interpreter.

**Status:** `[ ] pending`

---

### Sub-Task 7 — Narrative Printer and Terminal Display

**Intent:** Implement the narrative output system using the `rich` library to produce styled, readable terminal output — event prose in formatted text panels, periodic meter state summaries as color-coded tables.

**Expected Outcomes:**
- `narrative.py` contains `NarrativePrinter` class
- Event narrative prints as a styled panel with year, title, and prose body
- State summary prints as a table with meter names, values, and color-coded bars (green/yellow/red)
- Divergence branch points print in a visually distinct color (red border)
- Final ending prints a full-width styled conclusion panel

**Display Design (approximate):**
```
+-----------------------------------------------------+
|  1948 -- LeMay Takes Command of SAC                 |
+-----------------------------------------------------+
|  LeMay walks into SAC headquarters and immediately  |
|  fires three base commanders before dinner...       |
+-----------------------------------------------------+

  STATE SUMMARY -- 1948
  +----------------------+-------+--------------------+
  | Meter                | Value | Trend              |
  +----------------------+-------+--------------------+
  | Civilian Oversight   |  78   | XXXXXXXX.. down    |
  | Escalation Risk      |  22   | XX........ up      |
  +----------------------+-------+--------------------+
```

**Todo List:**
1. Implement `NarrativePrinter` with `print_event(event)`, `print_summary(year, meters)`, `print_divergence(divergence)`, `print_ending(ending)`
2. Use `rich.panel.Panel` for event display
3. Use `rich.table.Table` for state summaries with color-coded values (green > 60, yellow 30-60, red < 30 — inverted for `escalation_risk`)
4. Add trend arrows by comparing current meter value to previous turn's value
5. Add `--no-color` flag that disables rich styling for plain text output
6. Test display output manually by running `main.py`

**Relevant Context:** The `rich` library handles all terminal styling. No curses or complex TUI framework needed. Output should be clean enough to pipe to a log file if `--no-color` flag is passed.

**Status:** `[ ] pending`

---

## Endings

The simulation has four possible endings, defined by the final meter state in 1991:

| Ending ID | Condition | Title |
|---|---|---|
| `cold_war_won` | `civilian_oversight < 30` AND `escalation_risk < 40` | "The Quiet Surrender" — The U.S. wins the Cold War. Civilian oversight is a polite fiction. |
| `ww3_nuclear` | `escalation_risk > 90` | "The Stone Age" — LeMay's doctrine is vindicated, but there is no one left to celebrate. |
| `soviet_victory` | `public_support < 20` AND `defense_budget_share < 20` | "The Long Defeat" — Political restraint bleeds the military dry. The USSR outlasts the republic. |
| `oversight_restored` | `civilian_oversight > 70` in 1991 | "The Road Not Taken" — An unlikely outcome. Democracy holds. |

The default historical run always produces `cold_war_won`.

---

## Non-Goals

- No GUI, web interface, or graphical display
- No multiplayer or networked play
- No AI/LLM integration for dynamic narrative generation
- No save/load system (simulation is short enough to re-run)
- No historical figures added beyond the core six for this initial build
