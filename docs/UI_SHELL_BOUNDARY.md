# Local Read-only UI Shell Boundary

## 2. Purpose

Define what a future local UI shell may and may not do. This document is a
boundary contract only. It does not implement a UI shell, a frontend framework,
a backend, or any runtime script.

## 3. Current baseline

- The Phase 4E static demo command exists:
  `bash scripts/dev/run_phase4e_demo_bundle.sh 2026-W26`.
- The demo bundle is generated from existing artifacts.
- No backend exists.

## 4. Architecture boundary

- The vault is the governed source layer.
- The tmp artifacts are scrubbed, read-only projections.
- A future UI shell is a local view over approved static projections only.
- No direct vault reads.
- No vault writes.

## 5. Preferred future data sources

- `tmp/phase4b-ui-snapshot/manifest.json`
- `tmp/phase4b-ui-snapshot/index.html` as a static local demo target only
- `tmp/phase4c-snapshot-catalog/catalog.json`
- `tmp/phase4d-demo-verifier/verification-summary.json`
- `tmp/phase4e-demo-bundle/demo-bundle-summary.json`

## 6. Legacy/reference-only data sources

- `tmp/phase3b-portfolio-dashboard/portfolio-<week>.md`
- `tmp/phase3a-dashboard/dashboard-*-<week>.md`
- `tmp/phase2e-import-score-report/scores/*.json`

## 7. Rule for legacy/reference-only data sources

- A future UI shell should not read these directly unless a later phase
  explicitly adds a guardrail test and a documented reason.
- If score JSON is ever used as a fallback, `input_path` and `note_refs` must
  never be emitted.

## 8. Forbidden data sources

- `vault/`
- private notes
- raw unsanitized artifacts
- database
- environment credentials
- secrets
- external APIs
- external URLs
- marketplace connectors
- live marketplace data

## 9. Allowed future UI functions

- display snapshot status
- display catalog status
- display verification status
- display demo readiness
- link to local static snapshot files with relative links
- show guardrail status

## 10. Forbidden future UI functions

- approvals
- promote
- create decision
- finalize decision
- write vault
- edit artifacts
- generate affiliate content
- autopublish
- launch campaigns
- call external APIs
- ingest marketplace data

## 11. Forbidden implementation choices in Phase 5A

- Next.js
- React
- Vite
- package.json changes
- npm-based dependency install
- frontend framework
- backend service
- FastAPI
- server
- API routes
- database

## 12. Security guardrails

- HTML-escape all dynamic fields in any future implementation.
- No external URLs.
- No secrets.
- No vault paths.
- No raw artifact body.
- No approval mutation.
- No external connectors.
- No script-based network fetch unless a later phase explicitly permits and
  tests it.

## 13. Future implementation gates

- Phase 5B may create a local static shell prototype only if it reads Phase 4
  outputs as source of truth.
- Phase 5C may add a shell verifier / acceptance pack.
- Phase 5D may add an operator command for a shell demo.
- Phase 5E may update the release snapshot.
- A backend, an API, or a database must each be a separate future phase.

## 14. Known limitations

- Boundary doc only.
- No UI shell yet.
- No live refresh.
- No production deployment.

## Status

Phase 5A is documentation and contract-tests only. No UI shell implementation
exists yet.
