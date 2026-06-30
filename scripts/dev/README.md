# Dev Scripts

- `python scripts/dev/score_product.py vault/samples/products/smart-desk-pad.md --pretty`
- `python scripts/dev/generate_weekly_report.py --input-dir vault/samples --report-week 2026-W26`
- `bash scripts/dev/run_phase3a_dashboard_summary.sh prod-laptop-stand 2026-W26 [--write]`
- `bash scripts/dev/run_phase3b_portfolio_dashboard.sh 2026-W26 [--top N] [--write]`
- `bash scripts/dev/command_center.sh <help|status|doctor|dry-run|product|portfolio> [args...]`
- `bash scripts/dev/run_phase3d_acceptance.sh [<csv_path> <week> <product_id>]`
- `bash scripts/dev/show_release_snapshot.sh`
- `bash scripts/dev/run_phase4a_ui_mock.sh 2026-W26`
- `bash scripts/dev/run_phase4b_ui_snapshot.sh 2026-W26`
- `bash scripts/dev/run_phase4c_snapshot_catalog.sh`
- `bash scripts/dev/run_phase4d_demo_verifier.sh`
- `bash scripts/dev/run_phase4e_demo_bundle.sh 2026-W26`
- `bash scripts/dev/run_phase5b_ui_shell.sh 2026-W26`
