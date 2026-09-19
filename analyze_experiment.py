"""
Analyzes the simulated experiment: a two-proportion z-test on the primary
metric (trial-to-paid conversion), plus a check on the guardrail metric
(early cancellation rate), with confidence intervals on the lift.
"""

import math
import pandas as pd
from statsmodels.stats.proportion import proportions_ztest

df = pd.read_csv("data/experiment_results.csv")

control = df[df["group"] == "control"]
treatment = df[df["group"] == "treatment"]

# ---- Primary metric: trial-to-paid conversion ----
conv_counts = [treatment["converted"].sum(), control["converted"].sum()]
conv_nobs = [len(treatment), len(control)]

z_stat, p_value = proportions_ztest(conv_counts, conv_nobs, alternative="two-sided")

control_rate = control["converted"].mean()
treatment_rate = treatment["converted"].mean()
lift_abs = treatment_rate - control_rate
lift_rel = lift_abs / control_rate

# 95% CI on the absolute lift (difference of two independent proportions)
se_diff = math.sqrt(
    control_rate * (1 - control_rate) / len(control)
    + treatment_rate * (1 - treatment_rate) / len(treatment)
)
ci_low = lift_abs - 1.96 * se_diff
ci_high = lift_abs + 1.96 * se_diff

print("=== Primary Metric: Trial-to-Paid Conversion ===")
print(f"Control:   {control_rate:.2%}  (n={len(control):,})")
print(f"Treatment: {treatment_rate:.2%}  (n={len(treatment):,})")
print(f"Absolute lift: {lift_abs:+.2%}  (95% CI: [{ci_low:+.2%}, {ci_high:+.2%}])")
print(f"Relative lift: {lift_rel:+.1%}")
print(f"z-statistic: {z_stat:.3f}")
print(f"p-value:     {p_value:.4f}")
print(f"Result: {'STATISTICALLY SIGNIFICANT' if p_value < 0.05 else 'NOT significant'} at alpha=0.05")

# ---- Guardrail metric: early cancellation rate ----
print("\n=== Guardrail Metric: Cancelled Before Day 3 ===")
cancel_counts = [treatment["cancelled_before_day3"].sum(), control["cancelled_before_day3"].sum()]
cancel_nobs = [len(treatment), len(control)]
cz_stat, cp_value = proportions_ztest(cancel_counts, cancel_nobs, alternative="two-sided")

control_cancel_rate = control["cancelled_before_day3"].mean()
treatment_cancel_rate = treatment["cancelled_before_day3"].mean()

print(f"Control:   {control_cancel_rate:.2%}")
print(f"Treatment: {treatment_cancel_rate:.2%}")
print(f"p-value:   {cp_value:.4f}")
print(f"Result: {'Guardrail BREACHED (treatment made this worse)' if (cp_value < 0.05 and treatment_cancel_rate > control_cancel_rate) else 'Guardrail holds -- no significant harm detected'}")

print("\n=== Recommendation ===")
if p_value < 0.05 and treatment_rate > control_rate and not (cp_value < 0.05 and treatment_cancel_rate > control_cancel_rate):
    print("Ship the Quick-Start Checklist: it drives a statistically significant lift")
    print("in trial-to-paid conversion with no guardrail regression.")
else:
    print("Do not ship as-is -- either no significant lift, or a guardrail regression.")