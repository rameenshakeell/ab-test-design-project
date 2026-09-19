"""
Sample size / power calculation for the trial-to-paid conversion A/B test.

Scenario: a B2B SaaS product's free trial. Right now, users land in an empty
dashboard after signing up. The proposed change is a "Quick-Start Checklist"
shown immediately after signup, nudging users toward the 3 actions that
correlate with activation (invite a teammate, create a project, connect an
integration).

Hypothesis: showing the checklist increases the trial-to-paid conversion
rate, because it pushes more users to actually experience the product's
core value within the 14-day trial window instead of getting lost.
"""

from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

# ---- Assumptions ----
baseline_rate = 0.18       # current trial-to-paid conversion rate
mde_absolute = 0.04        # smallest lift worth shipping the feature for (+4pp)
target_rate = baseline_rate + mde_absolute
alpha = 0.05                # two-sided significance level
power = 0.80                # standard target power

effect_size = proportion_effectsize(target_rate, baseline_rate)

analysis = NormalIndPower()
n_per_group = analysis.solve_power(
    effect_size=effect_size,
    alpha=alpha,
    power=power,
    ratio=1.0,
    alternative="two-sided",
)

n_per_group = int(round(n_per_group))

print("=== Sample Size / Power Calculation ===")
print(f"Baseline conversion rate: {baseline_rate:.1%}")
print(f"Target conversion rate:   {target_rate:.1%}  (MDE = +{mde_absolute:.1%} absolute)")
print(f"Alpha (two-sided):        {alpha}")
print(f"Power:                    {power:.0%}")
print(f"Effect size (Cohen's h):  {effect_size:.4f}")
print(f"Required sample size:     {n_per_group:,} per group  ({n_per_group*2:,} total)")