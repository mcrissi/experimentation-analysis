# P1 — Experimentation Analysis (spec)

**Repo:** `experimentation-analysis` · **Package:** `xpa` · **CLI:** `uv run xpa …`
**Signals to a hiring manager:** decision-science rigor, causal thinking, and turning statistics into a business recommendation.

## Question
In the Hillstrom e-mail experiment, did the Mens or Womens campaign increase visits, conversions and spend versus no e-mail? For whom? What would we ship?

## Scope
**In:** experiment-health checks, frequentist effect estimation, variance reduction, power and design, peeking and sequential testing (simulation), exploratory heterogeneous effects, a decision memo, and a small reusable `xpa` library.
**Out:** Bayesian A/B (optional stretch), bandits, dashboards.

## Metrics (pre-registered in `docs/decisions/0001-metrics.md` before looking at outcomes)
- **Primary:** `visit` rate.
- **Secondary:** `conversion` rate, `spend` per customer.
- **Guardrail:** none native. State this limitation (e.g., unsubscribes aren't observed).
- Comparisons: Mens vs control and Womens vs control, with Holm correction across the 2 comparisons × primary metric.

## Phases and gates
| Phase | Work | Gate (must be true to proceed) |
|---|---|---|
| 0 Scaffold | Repo from templates, CI, `data/download.py`, `MANIFEST.json`, ADR 0001 (metrics) | CI green; data downloads with a checksum |
| 1 Health checks | **SRM** chi-square test; covariate balance (standardized mean differences on pre-treatment vars); missing/outlier audit on `spend` | SRM p-value and SMD table in `reports/results/health.json`; any imbalance explained |
| 2 Primary analysis | Two-proportion z-test + CI for the difference; relative lift with a delta-method CI; `spend` via bootstrap (zero-inflated, heavy-tailed) and a Welch comparison; Holm correction | Functions unit-tested against `statsmodels`; effects table with CIs |
| 3 Variance reduction | **CUPED** with `history` (and `recency`) as pre-period covariates; regression adjustment (Lin 2013) with robust SEs; report the CI-width reduction % | Same point estimate within noise; narrower CI quantified |
| 4 Design and peeking | MDE / power curves by sample size; **A/A simulation** (Type I error ≈ 5%); simulation showing false-positive inflation from daily peeking; one fix: group-sequential (O'Brien-Fleming alpha spending) or mSPRT | A/A FPR within [4%, 6%] over ≥ 2,000 sims; peeking chart |
| 5 Heterogeneity (exploratory) | Segment effects (`newbie`, `channel`, `zip_code`, `history_segment`) with Holm; uplift model (T-learner or X-learner) + Qini curve on a held-out split | Clearly labeled exploratory; the Qini curve beats random on held-out data, or the finding is reported as null |
| 6 Write-up | Decision memo (`reports/decision_memo.md`): recommendation, expected impact with a CI, risks, next experiment. README per template | Definition of done in `00` met; tag `v0.1.0` |

## `xpa` library surface (minimum)
```python
srm_test(counts: dict[str,int], expected_ratio: dict[str,float]) -> TestResult
diff_proportions(x_t, n_t, x_c, n_c, alpha=0.05) -> EffectResult
bootstrap_diff(y_t, y_c, stat="mean", n_boot=5000, seed=...) -> EffectResult
cuped_adjust(y, x_pre, theta=None) -> np.ndarray
power_two_proportions(p_base, mde, alpha, power) -> int
simulate_aa(n, p, n_sims, seed) -> float  # empirical FPR
```

## Acceptance criteria
- Every stats function has a test against a reference implementation or a closed-form value.
- The README headline is one table: arm × metric → lift, 95% CI, adjusted p, CUPED CI-width reduction.
- Key figure: forest plot of lifts with CIs (raw vs CUPED).
- The decision memo is ≤ 1 page, written for a non-technical PM.

## Risks
- The dataset is old (2008) and US retail. Frame it as a methods showcase and say so.
- Heterogeneity analysis invites p-hacking. Keep it corrected and labeled exploratory.
