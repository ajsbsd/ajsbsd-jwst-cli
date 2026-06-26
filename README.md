# Cold War Erosion Simulation

A Python data-driven narrative engine simulating the Cold War (1947–1991) and the permanent erosion of civilian oversight of the U.S. military.

## Thesis

Civilian control of the U.S. military was irreversibly eroded between 1947 and 1991 through four mechanisms:

1. **Technological Dependence** — Weapons became too complex for civilians to understand or oversee.
2. **Information Monopoly** — The military controlled all intelligence and metrics, feeding civilians the data they wanted to see.
3. **Economic Hostage-Taking** — The Military-Industrial Complex made the entire civilian economy dependent on perpetual defense spending.
4. **The Crisis Ratchet** — Every time civilian restraint caused a setback, the military used the failure to strip away the next layer of oversight.

## Setup

```bash
pip install -r requirements.txt
```

## Running the Simulation

```bash
python main.py
```

### Options

| Flag | Description |
|---|---|
| `--seed N` | Set a random seed for reproducible runs |
| `--verbose` | Print state summary every year instead of every 4 years |
| `--no-color` | Disable rich terminal styling (plain text, pipe-safe) |

## Architecture

```
simulation/
  engine.py        Main turn loop (1947–1991)
  figures.py       Figure dataclass + FigureRegistry
  events.py        Event dataclass + EventEngine
  meters.py        GlobalMeters dataclass
  narrative.py     NarrativePrinter (rich terminal output)
  data/
    figures/       YAML files — one per historical figure
    events/        YAML files — one per era (5 eras)
    divergence/    YAML files — alternate timeline branches
main.py            CLI entry point
```

## Historical Figures

- General Curtis E. LeMay (USAF / SAC Commander)
- Senator Joseph McCarthy
- President Harry S. Truman
- President Dwight D. Eisenhower
- Secretary of Defense Robert McNamara
- President Lyndon B. Johnson
- President Ronald Reagan

## Possible Endings

| Ending | Condition |
|---|---|
| **The Quiet Surrender** (default) | Cold War won, civilian oversight is a polite fiction |
| **The Stone Age** | Escalation triggers nuclear war |
| **The Long Defeat** | Political restraint starves the military; USSR outlasts the republic |
| **The Road Not Taken** | Civilian oversight is restored (nearly impossible on default settings) |

## Data Schema

See [SCHEMA.md](SCHEMA.md) for the full YAML schema for figures, events, and divergence branches.
