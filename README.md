# Cold War Erosion Simulation

A data-driven historical narrative simulation exploring the gradual erosion of civilian oversight of the United States military during the Cold War (1947–1991).

The simulation combines historical events, key political and military figures, global state meters, and alternate-history divergence paths to model how institutions evolve under sustained geopolitical pressure.

---

## Thesis

The simulation is built around four reinforcing mechanisms:

1. **Technological Dependence**
   Military systems become too specialized for meaningful civilian oversight.

2. **Information Monopoly**
   Intelligence, metrics, and threat assessments increasingly originate from military institutions themselves.

3. **Economic Hostage-Taking**
   Defense spending becomes structurally embedded in the broader economy.

4. **The Crisis Ratchet**
   Every perceived failure of restraint becomes justification for reducing future civilian control.

The result is not necessarily dictatorship, but a gradual shift in where real decision-making power resides.

---

## Features

* Historical timeline from **1947–1991**
* Data-driven event system powered by YAML
* Historical figures with traits, influence, and relationships
* Global state meters that evolve over time
* Alternate-history divergence branches
* Multiple endings
* Reproducible simulations via random seeds
* Event forcing and meter overrides for scenario testing
* Rich terminal output with optional plain-text mode

---

## Installation

### Requirements

* Python 3.10+
* pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Quick Start

Run a standard simulation:

```bash
python main.py
```

Run with a fixed random seed:

```bash
python main.py --seed 42
```

Print yearly summaries instead of four-year snapshots:

```bash
python main.py --verbose
```

Disable terminal styling:

```bash
python main.py --no-color
```

---

## CLI Options

| Flag                     | Description                                |
| ------------------------ | ------------------------------------------ |
| `--seed N`               | Use a deterministic random seed            |
| `--verbose`              | Print state summaries every year           |
| `--no-color`             | Disable Rich terminal styling              |
| `--list-events`          | Show every available event ID and exit     |
| `--force-event EVENT_ID` | Force an event to fire at simulation start |
| `--set-meter NAME=VALUE` | Override an initial meter value            |

---

## Listing Events

Display all event IDs:

```bash
python main.py --list-events
```

Example output:

```text
ID                                       YEAR   TITLE
-------------------------------------------------------
air_force_independence_1947              1947   The Air Force Becomes Independent
berlin_airlift_1948                      1948   The Berlin Airlift
sac_takeover_1948                        1948   LeMay Takes Command of SAC
...
```

This is useful when experimenting with forced scenarios.

---

## Forcing Historical Events

Force one or more events to occur before the simulation begins:

```bash
python main.py \
  --force-event sac_takeover_1948
```

Multiple events may be specified:

```bash
python main.py \
  --force-event sac_takeover_1948 \
  --force-event north_korea_invades_1950
```

Forced events ignore normal year and condition checks.

---

## Overriding Starting Conditions

Meters can be modified before the simulation starts:

```bash
python main.py \
  --set-meter escalation_risk=80
```

Multiple overrides are supported:

```bash
python main.py \
  --set-meter civilian_oversight=40 \
  --set-meter escalation_risk=75 \
  --set-meter information_monopoly=60
```

This allows rapid testing of alternate timelines and divergence branches.

---

## Core Meters

| Meter                      | Description                                        |
| -------------------------- | -------------------------------------------------- |
| `civilian_oversight`       | Effective civilian control over military decisions |
| `escalation_risk`          | Risk of nuclear escalation or global war           |
| `public_support`           | Public support for military spending and policy    |
| `defense_budget_share`     | Political and economic weight of defense spending  |
| `sac_readiness`            | Strategic Air Command readiness                    |
| `soviet_threat_perception` | Perceived Soviet threat level                      |
| `information_monopoly`     | Military control over intelligence and metrics     |
| `economic_dependence`      | Civilian dependence on defense spending            |

---

## Historical Figures

The simulation includes historical actors such as:

* Curtis E. LeMay
* Harry S. Truman
* Dwight D. Eisenhower
* Joseph McCarthy
* Robert McNamara
* Lyndon B. Johnson
* Ronald Reagan

Figures possess:

* Traits
* Relationships
* Influence statistics
* Active historical periods
* Decision archetypes

---

## Divergence Branches

Under certain conditions, the simulation can leave the historical timeline and enter alternate-history branches.

Included scenarios:

* Nuclear escalation in Korea (1951)
* Cuban crisis escalation (1962)
* Unrestricted Vietnam escalation (1965)

Each branch can introduce:

* Custom event chains
* Additional meter changes
* Unique endings

---

## Possible Endings

### The Quiet Surrender

The Cold War is won, but civilian oversight survives only as a formality.

### The Stone Age

Escalation spirals into nuclear war.

### The Long Defeat

Political restraint and declining support allow the Soviet bloc to outlast the American system.

### The Road Not Taken

Civilian oversight is restored and institutional balance survives.

---

## Project Structure

```text
simulation/
├── engine.py
├── events.py
├── figures.py
├── divergence.py
├── meters.py
├── narrative.py
│
└── data/
    ├── events/
    │   ├── era_1947_1953.yaml
    │   ├── era_1953_1961.yaml
    │   ├── era_1961_1968.yaml
    │   ├── era_1968_1980.yaml
    │   └── era_1980_1991.yaml
    │
    ├── figures/
    │   ├── truman.yaml
    │   ├── eisenhower.yaml
    │   ├── lemay.yaml
    │   ├── mccarthy.yaml
    │   ├── mcnamara.yaml
    │   ├── johnson.yaml
    │   └── reagan.yaml
    │
    └── divergence/
        ├── korea_nuclear_1951.yaml
        ├── cuba_airstrikes_1962.yaml
        └── vietnam_unrestricted_1965.yaml

main.py
SCHEMA.md
```

---

## Data-Driven Design

Most simulation behavior is defined outside Python code.

New content can be added by editing YAML files:

* Historical figures
* Events
* Meter effects
* Conditions
* Divergence branches
* Alternate endings

See:

```text
SCHEMA.md
```

for complete schema documentation.

---

## Example Experiments

### Trigger a Near-Nuclear Timeline

```bash
python main.py \
  --set-meter escalation_risk=85 \
  --set-meter civilian_oversight=35
```

### Force a Specific Crisis

```bash
python main.py \
  --force-event north_korea_invades_1950
```

### Explore Branch Outcomes

```bash
python main.py \
  --verbose \
  --set-meter escalation_risk=80
```

---

## License

See `LICENSE` for licensing information.
