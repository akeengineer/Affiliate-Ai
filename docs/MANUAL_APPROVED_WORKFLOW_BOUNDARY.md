# Manual Approved Workflow Boundary (Phase 6A)

## 1. Purpose

Define the contract for how future manual-approved workflows may move from
read-only artifacts into human-gated approval review, while preserving every
current guardrail. Phase 6A is a boundary contract only — docs/tests/task-only.
It implements no packet generation, no approval command, and no mutation; it
executes none of the existing manual-approved primitives.

## 2. Boundary model

```text
read-only tmp artifacts
-> approval review packet under tmp
-> human gate
-> existing manual-approved primitive
-> vault write only when explicit approval is provided
```

Each arrow is a future, separately approved step. Phase 6A defines the contract
for this chain and nothing more: there is no review-packet generator, no human
gate command, and no primitive invocation in this phase.

## 3. Source artifacts allowed into future approval review

These read-only inputs may be summarized into a future review packet. All are
`tmp/` artifacts or read-only summaries; no vault read is ever introduced.

- Phase 2E score JSON and weekly report (`tmp/phase2e-import-score-report/`)
- Phase 2F Hermes operational summary (`tmp/phase2f-hermes/`)
- Phase 2J governance summary (`tmp/phase2j-hermes-governance/`)
- Phase 3A dashboard output (`tmp/phase3a-dashboard/`)
- Phase 3B portfolio output (`tmp/phase3b-portfolio-dashboard/`)
- Phase 4E demo bundle summary (`tmp/phase4e-demo-bundle/`)
- Phase 5D UI shell demo summary (`tmp/phase5d-ui-shell-demo/`)
- Phase 5C verifier verdict (`tmp/phase5c-ui-shell-verifier/`)

## 4. Approval gates

Three human gates map to the existing manual-approved primitives. These
primitives are referenced as future targets only; Phase 6A does not run them.

### Promote gate

- future primitive: `promote_product_candidates.py`
- approval flag name: `APPROVE_PROMOTE`
- requires complete score evidence

### Decision gate

- future primitive: `create_decision.py`
- approval flag name: `APPROVE_DECISION`
- requires promoted candidate evidence

### Finalization gate

- future primitive: `finalize_decision.py`
- approval flag name: `APPROVE_FINALIZE`
- requires `compliance_status: approved`

### Mandatory ordering

```text
promote -> decision -> finalization
```

A gate may only be entered after the prior gate's evidence exists. No gate is
entered automatically, and none is reachable from the static UI shell.

## 5. Evidence requirements

A future review packet must include all of the following before any approval is
considered:

- `product_id`
- `report_week`
- `score_decision`
- `product_opportunity_score`
- `confidence_score`
- `compliance_status`
- verifier status / verifier verdict
- Phase 4D verification status
- Phase 5C verdict
- source artifact paths under `tmp/`
- operator identity placeholder
- approval reason
- timestamp in ISO-8601 UTC format

Incomplete evidence blocks approval. `compliance_status` must be `approved`
before finalization; any other value blocks the finalization gate.

## 6. Forbidden automation

The following are forbidden behaviors, not commands to run:

- autopublish
- campaign launch
- external API submit
- affiliate link generation
- hidden or implicit promotion
- direct approval from UI shell
- vault write without explicit approval flag
- finalization without `compliance_status: approved`
- marketplace connector
- backend / API / database
- network calls
- approval triggered from the static UI shell

## 7. Future Phase 6 roadmap

Documented as plan only; each is a separate future phase:

- Phase 6B: dry-run approval review packet under `tmp/phase6b-...`
- Phase 6C: manual approval command wrapping existing primitives, only after an
  explicit approval flag is provided
- Phase 6D: audit verifier over review packets and approval logs
- Phase 6E: release snapshot update

Backend, API, database, and marketplace features require separate future
approval and are outside this boundary.

## 8. Audit artifact concept

- review packets live under `tmp/phase6x-...` by default
- packets are immutable-style Markdown/JSON snapshots of the evidence
- no vault mutation by default
- approved writes must be explicit and logged

Each approval log entry must record:

- operator placeholder
- approval reason
- timestamp
- source artifact paths
- gate name
- outcome

## 9. Relation to the existing primitives

The Phase 2G/2H/2I primitives and their `APPROVE_*` flags remain unchanged.
Phase 6A neither modifies nor invokes them; it only documents how a future
phase would connect a reviewed, evidence-complete packet to a human gate before
those primitives are ever called.

## 10. Known limitations

- Boundary documentation only; there is no review packet, gate, or mutation yet.
- The operator identity is a placeholder; no authentication exists.
- Future Phase 6B+ are separate implementation phases under their own approval.

## Phase 6B dry-run review packet

Phase 6B implements the first read-only step inside this boundary: a dry-run
evidence packet builder. It reads only whitelisted scalar fields from existing
`tmp/` artifacts and writes a packet for future manual review.

```bash
bash scripts/dev/run_phase6b_approval_review_packet.sh prod-laptop-stand 2026-W26
```

Outputs:

- `tmp/phase6b-approval-review/review-prod-laptop-stand-2026-W26.json`
- `tmp/phase6b-approval-review/review-prod-laptop-stand-2026-W26.md`

The packet is **dry-run only and evidence only**: it does not approve, promote,
decide, finalize, or write the vault. It performs no vault reads or writes, no
approval mutation, and no primitive execution, and it makes no use of any
approval flag (the wrapper rejects approval flags). Gate readiness in the packet
is an evidence assessment, not permission to mutate.
