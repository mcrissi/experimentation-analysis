# {{Project title}}

{{One sentence: what question this repo answers and on what data.}}

## TL;DR
| {{rows: models/arms}} | {{metric 1 (95% CI)}} | {{metric 2}} | {{latency / cost}} |
|---|---|---|---|
| … | … | … | … |

![Key figure](reports/figures/{{key_figure}}.png)

**Key findings**
1. {{Finding with a number and CI}}
2. {{Finding}}
3. {{Negative / null result, if any}}

## Problem
{{Why this matters in a real business setting (2–4 sentences).}}

## Approach
{{Short description + optional diagram. Link docs/SPEC.md and ADRs for detail.}}

## Results
{{Full tables generated from reports/results/. Explain how to read each figure.}}

## Limitations
- {{Data caveats}}
- {{What would change the conclusion}}
- {{What wasn't tested}}

## Reproduce
```bash
git clone https://github.com/{{user}}/{{repo}} && cd {{repo}}
uv sync
cp .env.example .env   # add keys if you run the paid providers
uv run {{cli}} download
uv run {{cli}} run --all
uv run pytest
```
Paid API cost to reproduce everything: ~US${{x}} (cached results committed in `reports/results/`).

## Repository structure
{{tree -L 2}}

## Data and licenses
- Code: MIT.
- {{Dataset}}: {{license}}. Not redistributed; fetched by `download`.

## Author
{{AUTHOR_NAME}} · {{LinkedIn}} · {{email}}
