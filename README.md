# A/B Test Design: Trial-to-Paid Conversion Experiment

An end-to-end look at one feature, from requirements to results:

- **Requirements definition** — epic, user stories, acceptance criteria, and a process flow diagram, scoping what the feature needs to do before anyone builds or tests it (see [PRODUCT_REQUIREMENTS.md](PRODUCT_REQUIREMENTS.md))
- **Experiment design** — hypothesis, sample size/power calculation, and a primary + guardrail metric
- **Analysis** — synthetic data simulation and a real statistical test on the result


## The business problem

A B2B SaaS product runs a 14-day free trial. Right now, a user signs up and
lands on an empty dashboard — no guidance on what to do first. The team
suspects this hurts trial-to-paid conversion, because users who don't
quickly experience the product's core value tend to drift away and let the
trial expire.

**Proposed change:** show a "Quick-Start Checklist" immediately after
signup, nudging new users toward the three actions that most strongly
correlate with activation (invite a teammate, create a project, connect an
integration).

**Hypothesis:** showing the checklist increases trial-to-paid conversion,
because it pushes more users to actually reach the product's core value
within the trial window instead of getting lost.

**Primary metric:** trial-to-paid conversion rate (did the user convert to
a paid plan before their 14-day trial ended).

**Guardrail metric:** rate of cancelling the trial within the first 3 days
— a sign the checklist is overwhelming or annoying new users rather than
helping them, which would make the change net-negative even if conversion
went up.

## Methodology

**1. Sample size / power calculation** (`sample_size_calculation.py`)

Before collecting or simulating any data, the required sample size is
calculated from stated assumptions:

- Baseline conversion rate: 18%
- Minimum detectable effect: +4 percentage points (the smallest lift worth
  shipping the feature for)
- Significance level (alpha): 0.05, two-sided
- Power: 80%

This gives a required sample size of **1,566 users per group (3,132
total)** — the number of users you'd need to actually run this experiment
on before you could trust a result either way.

**2. Simulation** (`simulate_experiment.py`)

Since there's no real product behind this, user-level data for both groups
is simulated at the exact sample size the power calculation called for,
using a true underlying treatment effect (18% → 21.7%) plus randomness —
so the result behaves like a real, noisy experiment outcome rather than a
clean textbook example. The guardrail metric (early cancellation) is
simulated with no real difference between groups, to test whether the
analysis correctly avoids flagging a false guardrail breach.

**3. Analysis** (`analyze_experiment.py`)

Runs a two-proportion z-test on the primary metric with a 95% confidence
interval on the lift, and the same test on the guardrail metric, then
prints a ship/no-ship recommendation based on both results together.

## Result

| Metric | Control | Treatment | Result |
|---|---|---|---|
| Trial-to-paid conversion | 17.62% | 22.73% | +5.11pp lift (95% CI: +2.30% to +7.91%), p=0.0004 — **significant** |
| Cancelled before day 3 (guardrail) | 4.21% | 5.17% | p=0.21 — **not significant, guardrail holds** |

**Recommendation:** ship the Quick-Start Checklist. It drives a
statistically significant lift in trial-to-paid conversion with no
guardrail regression.

## Honest limitations

- All data is synthetic. The baseline rate, effect size, and guardrail
  rates are assumptions chosen to be realistic, not pulled from a real
  product.
- This simulates a single run of the experiment. In a real rollout, you'd
  also want to check for novelty effects (does the lift hold after week
  2-3, once the checklist stops being new) and segment the result by user
  type, since an aggregate lift can hide the change actually hurting one
  segment while helping another.
- Only one guardrail metric is tracked here. A real experiment usually
  monitors several (support ticket volume, feature adoption elsewhere,
  time-to-first-value) since a single guardrail can miss real harm
  elsewhere in the product.
- The two-proportion z-test assumes independent observations. In a real
  product, users referred by the same account or team aren't fully
  independent, which a more rigorous analysis would account for.

## Setup

```
pip install -r requirements.txt
python sample_size_calculation.py
python simulate_experiment.py
python analyze_experiment.py
```