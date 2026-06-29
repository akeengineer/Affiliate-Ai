# Task 020 - Phase 4A Local Read-only UI Mock

## 1. Purpose

Provide a local, read-only, static HTML mock over the artifacts the CLI already
generates (Phase 3B portfolio, Phase 3A dashboards, Phase 2E score JSON
fallback). It is a demo/visualization layer only — no server, API, database,
external resources, vault writes, or approval mutation.

## 2. Scope

- Generate one self-contained HTML file (inline CSS, zero JavaScript) from
  existing artifacts.
- Output to `tmp/phase4a-ui/index.html`, created idempotently.
- Degrade gracefully when artifacts are missing.

## 3. Files

Create:

- `codex/tasks/020-phase4a-local-readonly-ui-mock.md`
- `scripts/dev/build_ui_mock.py`
- `scripts/dev/run_phase4a_ui_mock.sh`
- `docs/UI_MOCK.md`
- `tests/test_phase4a_local_readonly_ui_mock.py`

Modify:

- `.gitignore` (add `tmp/phase4a-ui/`)
- `scripts/dev/README.md` (script index entry)

Do not modify Phase 2 or Phase 3A/3B/3C/3D/3E workflows unless a real bug is found.

## 4. Data sources

- `tmp/phase3b-portfolio-dashboard/portfolio-<week>.md` (portfolio counts)
- `tmp/phase3a-dashboard/dashboard-*-<week>.md` (per-product cards)
- `tmp/phase2e-import-score-report/scores/*.json` (fallback product list;
  never emit `input_path` or `note_refs`)

Promoted/decision/finalization counts come only from the scrubbed Phase 3B
artifact. The vault is never read directly.

## 5. Hard constraints

- no database, FastAPI, backend service, external APIs, affiliate content,
  autopublish, campaign launch, vault writes, approval mutation, Phase 2G/2H/2I
  triggering, or marketplace connector.
- read-only only; zero-JS self-contained static HTML; no external URLs/resources.

## 6. Acceptance criteria

- `build_ui_mock.py` compiles; `run_phase4a_ui_mock.sh` passes `bash -n`, is
  executable, and runs from a clean repo.
- Building writes `tmp/phase4a-ui/index.html` with header (incl. `READ-ONLY
  MOCK`), portfolio overview, top products, by-decision sections, per-product
  cards, and a guardrail footer.
- The HTML is self-contained: no `http://`/`https://`, `<script`, `fetch(`,
  `XMLHttpRequest`, `import(`, or external `<link>`.
- Generated HTML contains no private vault slash paths, affiliate URL patterns,
  secrets, or affiliate content markers (assert before write; fail otherwise).
- Dynamic fields are HTML-escaped; injected markup is neutralized.
- Missing artifacts degrade to a visible `no artifacts for <week>` notice, exit 0.
- Invalid week and unsafe guardrail flags fail non-zero.
- No vault writes occur.

## 7. Verification commands

```
python -m py_compile scripts/dev/build_ui_mock.py
bash -n scripts/dev/run_phase4a_ui_mock.sh
bash scripts/dev/run_phase3d_acceptance.sh
bash scripts/dev/run_phase4a_ui_mock.sh 2026-W26
source .venv/bin/activate && python -m pytest -q tests/test_phase4a_local_readonly_ui_mock.py
source .venv/bin/activate && python -m pytest -q
```

## 8. Known limitations

- Static snapshot; stale if artifacts are stale; no interactivity; no live
  refresh; no screenshots committed.
- Scores directory is not week-partitioned (fallback list is global); per-product
  cards and counts are week-scoped via the Phase 3A/3B artifacts.

## 9. Final status target

`phase4a_status: success`
