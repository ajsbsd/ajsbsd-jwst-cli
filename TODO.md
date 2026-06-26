### TODO.md

# Confirmed implemented

The repository now contains:

- `simulation/divergence.py`

- `simulation/engine.py`

- `simulation/events.py`

- `simulation/figures.py`

- `simulation/meters.py`

- `simulation/narrative.py`

plus the YAML data files and tests.

The CLI additions are genuinely present in `main.py`:

```bash
--list-events
--force-event EVENT_ID
--set-meter NAME=VALUE
```

and they're wired into the engine constructor.

---

# One thing I previously guessed incorrectly

I can now see the actual meter override code:

```python
current = self.meters.get(name)
self.meters.update(name, value - current)
```

That's not a bug; it's just an unusual implementation.

Functionally it works because:

```python
new_value = current + (target - current)
```

which equals:

```python
target
```

every time.

I'd still prefer:

```python
meters.set(name, value)
```

for readability, but the existing code is valid.

---

# Architecture observation

The forced events are executed **before** the main year loop:

```python
for event_id in self._force_events:
    event = self._find_event(event_id)
    ...
    self.event_engine.fire_event(...)
```

which means:

```bash
python main.py --force-event gulf_of_tonkin_1964
```

is not merely marking the event as eligible later—it is actually applying its outcomes to the starting state.

That's exactly how I'd implement a scenario injector.

---

# The biggest thing I'd add now

You have enough tooling that balancing is becoming harder than coding.

I'd strongly consider:

```bash
--debug-effects
```

with output like:

```text
1948 — LeMay Takes Command of SAC

sac_readiness:
20 → 40

civilian_oversight:
85 → 80

defense_budget_share:
30 → 38
```

Right now you can see yearly summaries, but you can't easily identify which specific event pushed a meter over a threshold.

Once you start tuning divergence branches, that becomes invaluable.

---

# Another useful flag

Given the new override system:

```bash
--show-start
```

or

```bash
--dump-state
```

before the run begins.

Example:

```text
INITIAL STATE

civilian_oversight     30 (OVERRIDE)
escalation_risk        80 (OVERRIDE)
public_support         70
defense_budget_share   30
...
```

That makes test runs reproducible and easier to discuss.

---

# What I would investigate next

The codebase itself looks healthy.

The question now is whether the simulation's *behavior* matches the README claim:

> The default historical run always produces "The Quiet Surrender."

From the outputs you've shown earlier, the simulation was reaching **The Stone Age** far too often.

So my next step wouldn't be more engine work.

I'd run:

```bash
python main.py --seed 1
python main.py --seed 2
python main.py --seed 3
...
```

and record:

- final ending

- final oversight

- final escalation

for perhaps 20 seeds.

If more than a small minority terminate in WW3, then the balancing—not the architecture—is where the work needs to happen. The framework is already mature enough that tuning event values and divergence thresholds will give you much more return than adding new features.
