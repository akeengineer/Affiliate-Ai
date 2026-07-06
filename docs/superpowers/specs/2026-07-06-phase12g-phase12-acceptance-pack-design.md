# Phase 12G Design — Phase 12 Acceptance Pack

## Objective

Create Phase 12G as a docs/tests-only Phase 12 acceptance/readiness pack after
Phase 12F.

Phase 12G must verify the full Phase 12A through Phase 12F chain while
remaining acceptance/readiness only. It must not implement runtime capability,
grant implementation approval, approve production promotion, bypass the Phase
7D selected-gate manual boundary, or select an approved runtime implementation
target.

## Design Direction

Phase 12G follows the Phase 12F pattern rather than the Phase 10F pattern.

The document shape is concise, boundary-first, and matrix-driven:

- compact top section with canonical acceptance boundary wording
- brief Phase 12A through Phase 12F acceptance summaries
- focused exclusion and boundary confirmation sections
- dense matrices carrying most acceptance evidence
- short ending sections for acceptance criteria, safe demos, operator
  checklist, and next-step guidance

Narrative supports the acceptance boundary but does not replace it.

## Required Outputs

Create:

- `codex/tasks/093-phase12g-phase12-acceptance-pack.md`
- `docs/PHASE12G_PHASE12_ACCEPTANCE_PACK.md`
- `tests/test_phase12g_phase12_acceptance_pack.py`

Update additively only:

- `docs/ROADMAP.md`
- `docs/PROJECT_STATE.md`
- `docs/PHASE12F_CONTROLLED_RUNTIME_IMPLEMENTATION_READINESS_PACK.md`

No runtime, infra, workflow, approval-record, or backend/API/database files may
be added or changed.

## Document Model

### Top of document

The opening sections must carry the canonical acceptance boundary and remain
easy to verify through exact-string tests.

The top of the document must make clear that Phase 12G is:

- acceptance/readiness only
- not production runtime
- not production promotion approval
- not implementation approval
- not a bypass of the Phase 7D selected-gate manual boundary
- not a selector or inference layer for an approved runtime implementation
  target

This boundary appears primarily in:

- `Phase 12G Purpose`
- `Phase 12 Acceptance Position`
- `Relationship to Phase 12A, Phase 12B, Phase 12C, Phase 12D, Phase 12E, and Phase 12F`
- `Phase 12 Chain Summary`

### Middle of document

The middle of the document remains brief and structured:

- `Phase 12A Acceptance Summary`
- `Phase 12B Acceptance Summary`
- `Phase 12C Acceptance Summary`
- `Phase 12D Acceptance Summary`
- `Phase 12E Acceptance Summary`
- `Phase 12F Acceptance Summary`
- focused exclusion sections for runtime, promotion, implementation approval,
  approved runtime domain status, Phase 7D manual boundary preservation,
  local-only prototype protection, RBAC advisory context confirmation, and
  runtime implementation target exclusion

Each phase summary is short and states what the phase defines without implying
runtime implementation or approval.

### Evidence model

Most acceptance evidence is carried by dense matrices, not long narrative.

Required matrices:

- `Phase 12 Acceptance Matrix`
- `Phase 12 Boundary Matrix`
- `Phase 12 Artifact Matrix`
- `Phase 12 Risk and Residual Control Matrix`
- `Phase 12 Verification Matrix`
- `Phase 12 Non-Goal Matrix`
- `Runtime Capability Exclusion Matrix`

These matrices repeat and reinforce the same boundary:

- readiness/acceptance only
- no runtime implementation
- no implementation approval
- no production promotion approval
- Phase 7D selected-gate manual boundary preserved
- Approved Runtime Domain still pending explicit Phase 12D approval unless a
  later explicit approval record exists

### Ending sections

The ending sections stay concise and subordinate to the acceptance boundary:

- `Acceptance Criteria`
- `Safe Demo Scenarios`
- `Operator Checklist`
- `Recommended Next Step`
- `Recommended Next Major Subphase`

These sections satisfy task requirements without turning Phase 12G into a long
operational checklist.

## File-by-File Implementation

### `docs/PHASE12G_PHASE12_ACCEPTANCE_PACK.md`

Implement as a compact acceptance/readiness document with:

- all required headings from the task brief
- exact canonical wording at the top and in key exclusion sections
- brief Phase 12A through Phase 12F summaries
- dense matrix sections carrying most acceptance proof
- explicit failure-handling model using fail-closed language
- concise operator and next-step sections

### `codex/tasks/093-phase12g-phase12-acceptance-pack.md`

Implement as the task record mirroring the nearby Phase 12 task pattern:

- status lines headed by `phase12g_status: success`
- purpose and relationship sections
- scope and non-goals
- preserved boundary wording
- acceptance criteria
- verification commands
- final status block

### `tests/test_phase12g_phase12_acceptance_pack.py`

Implement as a documentation-focused docs-contract test modeled on the Phase
12F test style.

Test scope:

- required files exist
- exact canonical wording exists
- required headings exist
- Phase 12A through Phase 12F references exist
- required matrices exist
- failure-handling model exists
- pointer updates reference Phase 12G
- repository-scope guards confirm no forbidden runtime, infra, key, signing,
  verifier, vault-client, backend/API/database, deployment, workflow, or
  implementation-approval artifacts were introduced by Phase 12G

## Pointer Updates

Pointer updates remain minimal and additive:

- `docs/PHASE12F_CONTROLLED_RUNTIME_IMPLEMENTATION_READINESS_PACK.md` gets a
  short forward pointer that Phase 12G verifies the full Phase 12A through
  Phase 12F chain as the acceptance/readiness pack
- `docs/ROADMAP.md` records Phase 12G as complete/done and describes it as the
  acceptance/readiness layer only
- `docs/PROJECT_STATE.md` records the current Phase 12 state without changing
  runtime posture

## Verification

Run exactly:

```bash
./.venv/bin/python -m pytest tests/test_phase12g_phase12_acceptance_pack.py -q
./.venv/bin/python -m pytest -q
git diff --check
git status --short
```

## Acceptance Constraints

The implementation must preserve all repo and task guardrails:

- no database
- no production runtime
- no backend/API/database files
- no deployment manifests
- no GitHub Actions workflows
- no production promotion automation
- no implementation approval record
- no approval-boundary bypass
- no approved runtime implementation target selection or inference

## Implementation Ready Outcome

Once implemented, Phase 12G should read as the final Phase 12 acceptance layer:

- concise
- boundary-first
- matrix-backed
- operationally light
- easy to verify with deterministic tests
