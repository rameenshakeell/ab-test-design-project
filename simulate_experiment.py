"""
Simulates user-level experiment data for the Quick-Start Checklist A/B test,
using the sample size from sample_size_calculation.py (1,566 per group).

This is synthetic data -- there's no real product behind this. The point is
to generate a dataset that behaves like a real experiment result (including
some noise) and then run a real statistical test against it.
"""

import csv
import random

random.seed(42)

N_PER_GROUP = 1566

# True underlying rates baked into the simulation. The treatment's true lift
# (18% -> 21.7%) is close to, but not exactly, the +4pp MDE we powered for --
# real effects rarely land exactly on the number you designed around.
TRUE_RATE = {
    "control": 0.18,
    "treatment": 0.217,
}

# Guardrail: rate of cancelling the trial in the first 3 days (a sign the
# checklist is overwhelming/annoying rather than helpful). Designed to show
# no real difference between groups.
TRUE_EARLY_CANCEL_RATE = {
    "control": 0.052,
    "treatment": 0.049,
}


def simulate_group(group_name, n):
    rows = []
    conv_rate = TRUE_RATE[group_name]
    cancel_rate = TRUE_EARLY_CANCEL_RATE[group_name]
    for i in range(n):
        user_id = f"{group_name[:4]}_{i:05d}"
        cancelled_early = random.random() < cancel_rate
        # a user who cancels in the first 3 days can't convert to paid
        if cancelled_early:
            converted = False
        else:
            converted = random.random() < (conv_rate / (1 - cancel_rate))
        rows.append({
            "user_id": user_id,
            "group": group_name,
            "converted": int(converted),
            "cancelled_before_day3": int(cancelled_early),
        })
    return rows


rows = simulate_group("control", N_PER_GROUP) + simulate_group("treatment", N_PER_GROUP)
random.shuffle(rows)

with open("data/experiment_results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["user_id", "group", "converted", "cancelled_before_day3"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Simulated {len(rows)} users ({N_PER_GROUP} per group) -> data/experiment_results.csv")