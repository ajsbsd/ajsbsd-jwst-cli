### AUTOMATION.md

To run 10,000 simulations and analyze the data statistically, you need to separate your **simulation engine** (the math and logic) from your **presentation layer** (the text/TTS output). 

For data analysis, the most "calculable" format is a **flat, event-level JSONL** (JSON Lines) file. Instead of one massive JSON object per run, you write one line per *event* per *run*. This allows you to easily load the data into Pandas, SQL, or Excel to calculate means, variances, and time-series trends.

Here is the blueprint for refactoring your simulator to achieve this.

### 1. The JSONL Schema (The "Calculable" Format)

Every time the simulation ticks forward a year or triggers an event, you write a single JSON object to the file. 

**Example of 3 lines in your `results.jsonl` file:**

```json
{"run_id": 1, "seed": 42, "year": 1947, "event": "air_force_independent", "civilian_oversight": 84, "escalation_risk": 15, "public_support": 78, "defense_budget": 40, "sac_readiness": 40, "soviet_threat": 40, "info_monopoly": 10, "econ_dependence": 15}
{"run_id": 1, "seed": 42, "year": 1948, "event": "berlin_airlift", "civilian_oversight": 84, "escalation_risk": 15, "public_support": 78, "defense_budget": 40, "sac_readiness": 40, "soviet_threat": 40, "info_monopoly": 10, "econ_dependence": 15}
{"run_id": 1, "seed": 42, "year": 1948, "event": "lemay_takes_sac", "civilian_oversight": 84, "escalation_risk": 15, "public_support": 78, "defense_budget": 40, "sac_readiness": 45, "soviet_threat": 40, "info_monopoly": 10, "econ_dependence": 15}
```

*Why this is powerful:* You can now instantly query: *"What is the average `civilian_oversight` in the year 1968 across all 10,000 runs?"*

---

### 2. The Command-Line Flags (`argparse`)

You need to add flags to `main.py` to tell the script to run silently in the background, execute $N$ times, and output to a file.

```python
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Cold War Erosion Simulator")

    # Presentation flags (your current mode)
    parser.add_argument("--tts", action="store_true", help="Output formatted for Text-to-Speech")
    parser.add_argument("--year", type=int, help="Stop simulation at a specific year")

    # Batch/Calculation flags (the new mode)
    parser.add_argument("--batch", action="store_true", help="Run in silent batch mode for data analysis")
    parser.add_argument("--runs", type=int, default=10000, help="Number of simulation runs to execute")
    parser.add_argument("--output", type=str, default="simulation_results.jsonl", help="Output file path")
    parser.add_argument("--seed", type=int, default=None, help="Base random seed for reproducibility")

    # Scenario flags (to test different historical variables)
    parser.add_argument("--no-lemay", action="store_true", help="Disable LeMay's SAC buildup")
    parser.add_argument("--no-mcnamara", action="store_true", help="Disable McNamara's systems analysis")

    return parser.parse_args()
```

---

### 3. Python Implementation (Memory-Efficient Batch Processing)

When running 10,000 simulations, **do not** store the results in a massive Python list and dump it at the end. Your RAM will spike. Instead, open the file and write line-by-line.

Here is how you structure the core loop in `main.py`:

```python
import json
import random
import sys
import uuid

def run_simulation_engine(run_id, seed, flags):
    """
    This is your pure logic engine. It yields the state at every event.
    It does NOT print anything to the console.
    """
    if seed is not None:
        random.seed(seed)

    # Initial State
    state = {
        "civilian_oversight": 100, "escalation_risk": 0, "public_support": 100,
        "defense_budget": 20, "sac_readiness": 10, "soviet_threat": 10,
        "info_monopoly": 0, "econ_dependence": 5
    }

    # Example timeline events
    timeline = [
        (1947, "air_force_independent"),
        (1948, "berlin_airlift"),
        (1948, "lemay_takes_sac"),
        # ... all the way to 1991
    ]

    for year, event in timeline:
        # 1. Apply event logic to state (with random variance based on seed)
        if event == "lemay_takes_sac" and not flags.get('no_lemay'):
            state["sac_readiness"] += random.randint(10, 20)
            state["civilian_oversight"] -= random.randint(2, 5)

        # 2. Yield the calculable record
        record = {
            "run_id": run_id,
            "seed": seed,
            "year": year,
            "event": event,
            **state # Unpacks all metrics into the root of the JSON
        }
        yield record

def main():
    args = parse_args()

    if args.batch:
        print(f"Starting batch run: {args.runs} simulations...", file=sys.stderr)

        # Open file in write mode. We will append line-by-line.
        with open(args.output, 'w', encoding='utf-8') as f:
            for i in range(args.runs):
                # Generate a unique seed for each run if a base seed is provided
                run_seed = (args.seed + i) if args.seed else random.randint(0, 2**32 - 1)

                # Run the engine and write each yielded event as a single JSON line
                for record in run_simulation_engine(i, run_seed, vars(args)):
                    f.write(json.dumps(record) + '\n')

                # Progress bar in stderr so it doesn't mess up data piping
                if (i + 1) % 1000 == 0:
                    print(f"Completed {i + 1}/{args.runs} runs...", file=sys.stderr)

        print(f"Done. Data saved to {args.output}", file=sys.stderr)

    else:
        # Your existing interactive/TTS presentation code goes here
        pass

if __name__ == "__main__":
    main()
```

---

### 4. How to Run It

Now you can execute your 10,000 runs from the terminal.

**Standard 10k run:**

```bash
python main.py --batch --runs 10000 --output cold_war_10k.jsonl --seed 42
```

**Testing a specific historical hypothesis (e.g., "What if McNamara never implemented Systems Analysis?"):**

```bash
python main.py --batch --runs 10000 --output no_mcnamara_10k.jsonl --no-mcnamara --seed 42
```

---

### 5. How to Calculate and Analyze the JSONL

Because the data is flat, analyzing it is incredibly easy. 

#### Option A: Using Python and Pandas (Recommended)

Pandas can read JSONL directly into a DataFrame.

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load the 10,000 runs (approx 400,000 rows)
df = pd.read_json('cold_war_10k.jsonl', lines=True)

# 1. What is the mean Civilian Oversight in 1991 across all runs?
final_oversight = df[df['year'] == 1991]['civilian_oversight'].mean()
print(f"Average Civilian Oversight in 1991: {final_oversight:.2f}")

# 2. What is the standard deviation? (How much does randomness affect the outcome?)
std_dev = df[df['year'] == 1991]['civilian_oversight'].std()
print(f"Standard Deviation: {std_dev:.2f}")

# 3. Plot the erosion of oversight over time (Mean of all 10k runs)
timeline_avg = df.groupby('year')['civilian_oversight'].mean()
timeline_avg.plot(title="Mean Civilian Oversight Erosion (10k Runs)")
plt.ylabel("Oversight Score")
plt.show()

# 4. Did the Gulf of Tonkin cause a statistically significant drop?
pre_tonkin = df[(df['year'] == 1962)]['civilian_oversight'].mean()
post_tonkin = df[(df['year'] == 1965)]['civilian_oversight'].mean()
print(f"Drop from Tonkin: {pre_tonkin - post_tonkin:.2f}")
```

#### Option B: Using `jq` in the Terminal (Quick Checks)

If you just want to quickly check the data without loading Python, use `jq`.

```bash
# Get the average civilian oversight in 1991 across all runs
jq -s '[.[] | select(.year == 1991) | .civilian_oversight] | add / length' cold_war_10k.jsonl

# Find the single run where civilian oversight was highest in 1991
jq -s '[.[] | select(.year == 1991)] | max_by(.civilian_oversight)' cold_war_10k.jsonl
```

### Summary of the Architecture

By adding the `--batch` and `--runs` flags, and yielding flat dictionaries to a JSONL file, you transform your project from a **narrative text generator** into a **Monte Carlo engine**. You can now mathematically prove your simulation's thesis: that the erosion of civilian oversight isn't just a narrative inevitability, but a statistical one driven by the mechanics of the system.
