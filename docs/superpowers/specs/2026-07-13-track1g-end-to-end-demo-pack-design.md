# Track 1G End-to-End Demo Pack Design

## Goal

Track 1G implements the end-to-end demo pack for the first usable local product slice.

The demo pack proves the local Track 1C/1D/1E/1F slice can run from storage reset
through Product and AffiliateOffer creation/listing, with a deterministic local
summary suitable for tests and operator review.

## Design Decision

Track 1G uses a dependency-free Python demo runner under `scripts/dev/` plus a
repo-consistent shell wrapper.

The runner is intentionally local and deterministic:

- it uses a local SQLite demo database path
- it resets and seeds storage through the Track 1D storage module
- it verifies runtime status through the existing backend status helper shape
- it verifies the Track 1F operator surface by rendering the operator page
- it creates Product and AffiliateOffer records through Track 1E service helpers
- it lists Product and AffiliateOffer results through Track 1E service helpers
- it writes/prints a stable JSON summary

## File Structure

- `scripts/dev/track1g_end_to_end_demo_pack.py`
  Core deterministic demo runner.
- `scripts/dev/run_track1g_end_to_end_demo_pack.sh`
  Shell wrapper matching existing `scripts/dev/run_*` conventions.
- `tests/test_track1g_end_to_end_demo_pack.py`
  Focused Track 1G tests.
- `codex/tasks/102-track1g-end-to-end-demo-pack.md`
  Task record.
- `docs/TRACK1G_END_TO_END_DEMO_PACK.md`
  Canonical Track 1G documentation.
- `docs/ROADMAP.md`, `docs/PROJECT_STATE.md`,
  `docs/TRACK1F_MINIMAL_USABLE_UI_OPERATOR_FLOW.md`
  State pointer updates.

## Runtime Status Delta

Track 1G extends `GET /runtime/status` with:

- `end_to_end_demo_pack_status: implemented in Track 1G`
- `demo_workflow_status: implemented in Track 1G`
- `production_demo_deployment_status: not approved`
- `insight_generation_status: not implemented in Track 1G`
- `recommendation_runtime_status: not implemented in Track 1G`

It preserves all local-only Track 1C/1D/1E/1F status fields.

## Demo Output Contract

The deterministic JSON summary includes:

- `runtime_mode`
- `storage_runtime`
- `product_core_api_status`
- `minimal_operator_flow_status`
- `demo_product_count`
- `demo_affiliate_offer_count`
- `demo_status: ok`

The runner may include additional deterministic details such as created IDs,
database path, and report path.

## Boundary

Track 1G does not implement production deployment, production authentication,
RBAC enforcement, production signing, verifier runtime, key custody runtime,
cloud infrastructure, CI/CD deployment, payment/billing, multi-tenant security,
customer production use, production promotion, or production deployment.
