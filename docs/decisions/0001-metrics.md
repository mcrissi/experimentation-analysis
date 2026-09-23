# ADR 0001: Pre-registered metrics and comparisons

- **Date:** 2026-09-23
- **Status:** accepted

## Context
The Hillstrom experiment randomized ~64k customers into three arms (Mens e-mail, Womens e-mail,
no e-mail) and tracked outcomes for two weeks. Choosing metrics or tests after seeing outcomes
inflates false positives (the garden of forking paths). This ADR fixes them **before any outcome
comparison between arms is computed**. It is committed before the first full data download; git
history is the evidence of that order.

## Options considered
1. Pre-register one primary metric plus secondaries, with a fixed multiplicity correction:
   pros: honest error control, clear decision metric / cons: less flexibility later.
2. Analyze all metrics equally and decide afterwards: pros: flexible / cons: invites p-hacking,
   no controlled error rate.

## Decision
Option 1, exactly as in `docs/SPEC.md`:

**Analysis population.** All randomized customers, analyzed in the arm they were assigned to
(intention-to-treat). Arms: `mens`, `womens`, `control`.

**Primary metric.** `visit` rate: share of customers with `visit = 1` in the 2-week window.

**Secondary metrics.**
- `conversion` rate: share of customers with `conversion = 1`.
- `spend` per customer: mean of `spend` over **all** customers in the arm, zeros included.

**Guardrail.** None available in the data. Unsubscribes, complaints and long-term effects are not
observed; this is a stated limitation, not a pass.

**Comparisons.** Mens vs control and Womens vs control (2 comparisons). Mens vs Womens is not a
pre-registered test.

**Tests and estimates** (two-sided, α = 0.05, 95% CIs):
- Rates: two-proportion z-test; CI for the absolute difference; relative lift with a delta-method CI.
- Spend: difference in means with a bootstrap CI (seeded) and a Welch test as a cross-check.

**Multiplicity.** Holm correction across the 2 comparisons for the primary metric. Secondary
metrics are reported with their CIs as supporting evidence and do not drive the decision alone.

**Out of scope for confirmatory claims.** Segment effects and uplift modeling (Phase 5) are
exploratory, Holm-corrected within their family, and labeled exploratory wherever reported.

## Consequences
- Any change to a metric, test or comparison needs a new ADR that supersedes this one and says why.
- Variance reduction (CUPED, regression adjustment; Phase 3) may change CIs but not the estimand or
  the primary metric.
- Until Phase 2, only arm sizes may be inspected; no outcome differences between arms.
