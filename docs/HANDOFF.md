# HANDOFF — experimentation-analysis

> Newest entry on top. Paste the latest entry into the Claude Desktop Project to update status.

---

## 2026-09-23 — Phase 0: Scaffold

**Status:** gate passed
**Branch / last commit:** `phase-0-scaffold` @ `2635be2` (PR #1 → `main`)
**Tests:** 21 passing, offline · **CI:** green (ubuntu + windows, run 35893023295)

### Done
- Package `xpa`: `Settings` (pydantic-settings: `data_dir`, `seed`), typer CLI (`download`, `clean`, `--version`). Deps per spec; `uv.lock` committed; Python 3.12.
- `xpa download`: tries the minethatdata original, then the sklift S3 mirror; one pinned sha256 per source; atomic write to `data/raw/hillstrom.csv`; `data/raw/MANIFEST.json` (source, URL, `retrieved_at` UTC, sha256, bytes, `n_rows`, columns, failed sources). Real run: `minethatdata`, 64,000 rows, sha256 `0e5893…aece`. Mirror verified separately (64,000 rows, `00a6a8…a2c0`).
- `xpa clean`: silver `data/processed/hillstrom.parquet` with typed columns, ordered `history_segment`, categoricals, `arm ∈ {control, mens, womens}` and schema assertions. Arm sizes: control 21,306 · mens 21,307 · womens 21,387.
- ADR 0001 (pre-registered metrics) committed **before** the first full download (`6384ab6` precedes `f909696`). ADR 0002 (data source).
- CI: `actions/checkout@v7`, `astral-sh/setup-uv` pinned to v10.2.0 by SHA, ruff + ruff format + pyright + pytest.
- Repo public at `mcrissi/experimentation-analysis`; all commits authored as `mcrissi` (noreply); push actor verified as `mcrissi` via the events API.

### Results produced
- None (Phase 0). No outcome differences between arms were computed or inspected.

### Decisions (link ADRs)
- [ADR 0001](decisions/0001-metrics.md): primary `visit`; secondary `conversion`, `spend` (all customers, zeros included); Mens vs control and Womens vs control; Holm across the 2 primary comparisons; ITT population.
- [ADR 0002](decisions/0002-data-source.md): the two public copies hold identical values but differ in formatting, so each source pins its own hash (the planned "same sha256 for the fallback" was not possible).
- `mens`/`womens` are **pre-treatment purchase flags, not assignment** (they're distributed alike across arms); `arm` comes from `segment` only. A test documents it.
- `setup-uv` publishes no floating major tags since v8 → pinned by commit SHA.
- `.env.example` trimmed to `DATA_DIR`, `XPA_SEED`.

### Open questions / risks
- ADR 0001 adds two details the spec leaves implicit: ITT population and spend averaged over all customers. Confirm in the Project.
- Source label `Surburban` kept as published (typo in the original data).
- Git pushes use a **repo-local credential helper** that serves `gh auth token --user mcrissi` (the machine's default Git Credential Manager and `gh auth git-credential` only serve the active work account). Needed again in P2–P4.

### Paid API spend this session
- Jev: US$0 · LLM: US$0 · cumulative: US$0

### Next step
- Merge PR #1 into `main`; then kickoff Phase 1 (SRM chi-square, covariate balance SMDs, `spend` audit → `reports/results/health.json`).

<!--
## YYYY-MM-DD — Phase N: NAME
**Status:** in progress | gate passed | blocked
**Branch / last commit:** `branch` @ `sha`
**Tests:** … · **CI:** …
### Done / Results produced / Decisions (link ADRs) / Open questions / risks / Paid API spend this session / Next step
-->
