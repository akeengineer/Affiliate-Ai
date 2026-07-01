from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
WRAPPER = REPO_ROOT / "scripts/dev/run_phase7b_audit_verifier.sh"
VERIFIER = REPO_ROOT / "scripts/dev/verify_manual_approval_audit.py"
TASK_FILE = REPO_ROOT / "codex/tasks/043-phase7b-audit-verifier.md"
GITIGNORE = REPO_ROOT / ".gitignore"

OUT_DIR = REPO_ROOT / "tmp/phase7b-audit-verifier"
FIX_DIR = OUT_DIR / "fixtures"
WEEK = "2026-W26"

VAULT_PRODUCTS_DIR = REPO_ROOT / "vault/products"
VAULT_DECISIONS_DIR = REPO_ROOT / "vault/decisions"

GUARDRAIL_FLAGS = [
    "APPROVE_PROMOTE",
    "APPROVE_DECISION",
    "APPROVE_FINALIZE",
    "ENABLE_AUTOPUBLISH",
    "ENABLE_OPENAI_API_DIRECT",
]

# Composed so this test source carries no contiguous operator-path literal.
OPERATOR_PATH = "/home/ubuntu/" + "Affiliate-Ai"
RAW_FORBIDDEN = ("http://", "https://", "AWS_SECRET_ACCESS_KEY", OPERATOR_PATH, "vault/", "../")

REF_PATHS = {
    "source_packet_path": "tmp/phase6b-approval-review",
    "verifier_path": "tmp/phase6c-approval-review-verifier",
    "execution_plan_path": "tmp/phase6e-approval-execution-plan",
}


def _base_env(**overrides: str) -> dict[str, str]:
    env = os.environ.copy()
    env.pop("AFFILIATE_REQUIRE_OPERATOR_RUNTIME", None)
    env.update(overrides)
    return env


def _run(*args: str, env: dict[str, str] | None = None, cwd: Path | None = None):
    return subprocess.run(
        ["bash", str(WRAPPER), *args], cwd=cwd or REPO_ROOT, capture_output=True, text=True, env=env or _base_env()
    )


def _ref(field: str, pid: str) -> str:
    stub = {"source_packet_path": "review", "verifier_path": "verification-review", "execution_plan_path": "plan"}[field]
    return f"{REF_PATHS[field]}/{stub}-{pid}-{WEEK}.json"


def _base_audit(pid: str, gate: str = "promote") -> dict:
    primitive = {"promote": "promote_product_candidates.py", "decision": "create_decision.py", "finalization": "finalize_decision.py"}[gate]
    flag = {"promote": "APPROVE_PROMOTE", "decision": "APPROVE_DECISION", "finalization": "APPROVE_FINALIZE"}[gate]
    return {
        "product_id": pid,
        "report_week": WEEK,
        "selected_gate": gate,
        "primitive_name": primitive,
        "operator": "op1",
        "approval_reason": "reviewed and approved",
        "timestamp": "2026-06-30T00:00:00Z",
        "source_packet_path": _ref("source_packet_path", pid),
        "verifier_path": _ref("verifier_path", pid),
        "execution_plan_path": _ref("execution_plan_path", pid),
        "precondition_summary": "preconditions ok",
        "result_summary": "completed",
        "outcome": "success",
        "mutation_attempted": False,
        "gate_specific_approval_intent": f"{gate}_only",
        "approved_flag_name": flag,
        "wrapper_version": "0.1",
        "audit_schema_version": "1",
    }


def _make_refs(pid: str) -> None:
    for field in REF_PATHS:
        p = REPO_ROOT / _ref(field, pid)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("{}", encoding="utf-8")


def _write(pid: str, audit, *, make_refs: bool = True, raw: str | None = None) -> str:
    FIX_DIR.mkdir(parents=True, exist_ok=True)
    if make_refs:
        _make_refs(pid)
    rel = f"tmp/phase7b-audit-verifier/fixtures/audit-{pid}.json"
    path = REPO_ROOT / rel
    path.write_text(raw if raw is not None else json.dumps(audit, indent=2), encoding="utf-8")
    return rel


def _out_json(pid: str, gate: str = "promote") -> Path:
    return OUT_DIR / f"audit-verification-{pid}-{WEEK}-{gate}.json"


# ── 1-5. existence / syntax / gitignore ───────────────────────────────────────

def test_artifacts_exist() -> None:
    assert WRAPPER.is_file()
    assert VERIFIER.is_file()
    assert TASK_FILE.is_file()
    assert "phase7b_status: success" in TASK_FILE.read_text(encoding="utf-8")


def test_wrapper_executable() -> None:
    assert os.access(WRAPPER, os.X_OK)
    assert (WRAPPER.stat().st_mode & 0o111), "wrapper must be executable"


def test_wrapper_syntax_ok() -> None:
    res = subprocess.run(["bash", "-n", str(WRAPPER)], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr


def test_verifier_compiles() -> None:
    res = subprocess.run(["python", "-m", "py_compile", str(VERIFIER)], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr


def test_gitignore_includes_phase7b() -> None:
    assert "tmp/phase7b-audit-verifier/" in GITIGNORE.read_text(encoding="utf-8")


# ── 6. valid paths ────────────────────────────────────────────────────────────

@pytest.mark.parametrize("gate", ["promote", "decision", "finalization"])
def test_valid_audit(gate: str) -> None:
    pid = f"prod-valid-{gate}"
    rel = _write(pid, _base_audit(pid, gate))
    res = _run(rel)
    assert res.returncode == 0, res.stderr
    assert "verdict: valid" in res.stdout
    data = json.loads(_out_json(pid, gate).read_text())
    assert data["verdict"] == "valid"
    assert data["failures"] == []


# ── 7-13. invalid: fields / json / mapping / mutation ─────────────────────────

def test_missing_required_field() -> None:
    pid = "prod-missing-field"
    audit = _base_audit(pid)
    del audit["operator"]
    res = _run(_write(pid, audit))
    assert res.returncode != 0
    assert "verdict: invalid" in res.stdout


def test_invalid_json() -> None:
    pid = "prod-bad-json"
    res = _run(_write(pid, None, raw="{not valid json"))
    assert res.returncode != 0
    assert "verdict: invalid" in res.stdout


def test_wrong_primitive_mapping() -> None:
    pid = "prod-wrong-prim"
    audit = _base_audit(pid)
    audit["primitive_name"] = "create_decision.py"
    assert _run(_write(pid, audit)).returncode != 0


def test_wrong_flag_mapping() -> None:
    pid = "prod-wrong-flag"
    audit = _base_audit(pid)
    audit["approved_flag_name"] = "APPROVE_DECISION"
    assert _run(_write(pid, audit)).returncode != 0


def test_blocked_with_mutation_true() -> None:
    pid = "prod-blocked-mut"
    audit = _base_audit(pid)
    audit["outcome"] = "blocked"
    audit["mutation_attempted"] = True
    assert _run(_write(pid, audit)).returncode != 0


def test_prevented_with_mutation_true() -> None:
    pid = "prod-prevented-mut"
    audit = _base_audit(pid)
    audit["outcome"] = "prevented"
    audit["mutation_attempted"] = True
    assert _run(_write(pid, audit)).returncode != 0


def test_success_missing_mutation() -> None:
    pid = "prod-missing-mut"
    audit = _base_audit(pid)
    del audit["mutation_attempted"]
    assert _run(_write(pid, audit)).returncode != 0


# ── 14-16. invalid input path ─────────────────────────────────────────────────

def test_absolute_input_path() -> None:
    assert _run("/etc/passwd").returncode != 0


def test_traversal_input_path() -> None:
    assert _run("tmp/../etc/x.json").returncode != 0


def test_vault_input_path() -> None:
    assert _run("vault/products/x.json").returncode != 0


# ── 17-19. invalid referenced path ────────────────────────────────────────────

def test_referenced_absolute_path() -> None:
    pid = "prod-ref-abs"
    audit = _base_audit(pid)
    audit["source_packet_path"] = "/etc/passwd"
    assert _run(_write(pid, audit)).returncode != 0


def test_referenced_traversal_path() -> None:
    pid = "prod-ref-trav"
    audit = _base_audit(pid)
    audit["verifier_path"] = "tmp/phase6c-approval-review-verifier/../../etc/x.json"
    assert _run(_write(pid, audit)).returncode != 0


def test_referenced_vault_path() -> None:
    pid = "prod-ref-vault"
    audit = _base_audit(pid)
    audit["execution_plan_path"] = "vault/decisions/x.md"
    assert _run(_write(pid, audit)).returncode != 0


# ── 20-24. invalid: forbidden body content ────────────────────────────────────

def test_external_url_in_audit() -> None:
    pid = "prod-url"
    audit = _base_audit(pid)
    audit["approval_reason"] = "see http" + "://example.test/x"
    assert _run(_write(pid, audit)).returncode != 0


def test_secret_marker_in_audit() -> None:
    pid = "prod-secret"
    audit = _base_audit(pid)
    audit["result_summary"] = "leaked AWS_SECRET_" + "ACCESS_KEY=abc"
    assert _run(_write(pid, audit)).returncode != 0


def test_approval_command_form_in_audit() -> None:
    pid = "prod-cmdform"
    audit = _base_audit(pid)
    audit["precondition_summary"] = "ran bash scripts/dev/run_phase2" + "g manually"
    assert _run(_write(pid, audit)).returncode != 0


def test_multi_gate_evidence() -> None:
    pid = "prod-multigate"
    audit = _base_audit(pid)
    audit["result_summary"] = "multi" + "-gate batch across promote and decision"
    assert _run(_write(pid, audit)).returncode != 0


def test_global_approval_evidence() -> None:
    pid = "prod-globalapprove"
    audit = _base_audit(pid)
    audit["gate_specific_approval_intent"] = "approve" + "-all gates"
    assert _run(_write(pid, audit)).returncode != 0


# ── 25-26. warning paths ──────────────────────────────────────────────────────

def test_missing_referenced_artifact_warns() -> None:
    pid = "prod-warn-missing"
    audit = _base_audit(pid)
    # safe expected-shape path, but do not create the referenced file
    rel = _write(pid, audit, make_refs=False)
    res = _run(rel)
    assert res.returncode == 0, res.stderr
    assert "verdict: warning" in res.stdout
    data = json.loads(_out_json(pid).read_text())
    assert data["verdict"] == "warning"
    assert any("referenced_artifact_missing" in w for w in data["warnings"])


def test_stale_schema_warns() -> None:
    pid = "prod-warn-stale"
    audit = _base_audit(pid)
    audit["audit_schema_version"] = "0"
    res = _run(_write(pid, audit))
    assert res.returncode == 0, res.stderr
    assert "verdict: warning" in res.stdout


# ── 27-31. wrapper guardrail flags ────────────────────────────────────────────

@pytest.mark.parametrize("flag", GUARDRAIL_FLAGS)
def test_wrapper_rejects_flag(flag: str) -> None:
    pid = "prod-flag"
    rel = _write(pid, _base_audit(pid))
    assert _run(rel, env=_base_env(**{flag: "true"})).returncode != 0


# ── 32. cross-CWD ─────────────────────────────────────────────────────────────

def test_cross_cwd_execution(tmp_path: Path) -> None:
    pid = "prod-crosscwd"
    rel = _write(pid, _base_audit(pid))
    res = _run(rel, cwd=tmp_path)
    assert res.returncode == 0, res.stderr
    assert "verdict: valid" in res.stdout


# ── 33. wrong arg count ───────────────────────────────────────────────────────

def test_wrong_arg_count_fails() -> None:
    assert _run().returncode != 0
    assert _run("tmp/a.json", "tmp/b.json").returncode != 0


# ── 34-36. output location / self-safety / category labels ────────────────────

def test_output_under_tmp_only() -> None:
    pid = "prod-outloc"
    _run(_write(pid, _base_audit(pid)))
    j = _out_json(pid)
    m = OUT_DIR / f"audit-verification-{pid}-{WEEK}-promote.md"
    assert j.is_file() and m.is_file()
    assert str(j.resolve()).startswith(str(OUT_DIR.resolve()) + os.sep)


def test_output_self_safety_and_category_labels() -> None:
    pid = "prod-selfsafe"
    audit = _base_audit(pid)
    audit["approval_reason"] = "see http" + "://x.test and AWS_SECRET_" + "ACCESS_KEY=z"
    _run(_write(pid, audit))
    j = _out_json(pid)
    m = OUT_DIR / f"audit-verification-{pid}-{WEEK}-promote.md"
    for f in (j, m):
        text = f.read_text(encoding="utf-8")
        for tok in RAW_FORBIDDEN:
            assert tok not in text, f"{f.name} leaked raw token: {tok}"
    data = json.loads(j.read_text())
    cats = data["forbidden_content"]["categories"]
    assert "external_url" in cats and "secret_marker" in cats
    assert data["forbidden_content"]["clean"] is False


# ── 37-39. no vault write / no primitive execution / input not mutated ────────

def _vault_snapshot() -> tuple[list[str], list[str]]:
    p = sorted(x.name for x in VAULT_PRODUCTS_DIR.iterdir()) if VAULT_PRODUCTS_DIR.is_dir() else []
    d = sorted(x.name for x in VAULT_DECISIONS_DIR.iterdir()) if VAULT_DECISIONS_DIR.is_dir() else []
    return p, d


def test_no_vault_write_or_primitive_execution() -> None:
    before = _vault_snapshot()
    pid = "prod-novault"
    _run(_write(pid, _base_audit(pid)))
    assert _vault_snapshot() == before, "verifier must not write vault or run primitives"


def test_input_not_mutated() -> None:
    pid = "prod-immutable"
    rel = _write(pid, _base_audit(pid))
    src = REPO_ROOT / rel
    before = hashlib.sha256(src.read_bytes()).hexdigest()
    _run(rel)
    assert hashlib.sha256(src.read_bytes()).hexdigest() == before, "input audit must not be rewritten"
