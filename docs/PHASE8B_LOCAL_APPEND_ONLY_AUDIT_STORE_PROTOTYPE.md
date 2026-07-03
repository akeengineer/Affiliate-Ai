# Phase 8B — Local Append-only Audit Store Prototype Compatibility Note

This compatibility note exists because Phase 10B references the Phase 8B audit
store prototype using the more explicit filename
`PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE_PROTOTYPE.md`, while the canonical Phase
8B implementation document remains
`docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md`.

Phase 10B actor attribution audit store integration planning may reference the
Phase 8B append-only audit store conceptually, preserves append-only and
hash-chain semantics, and does not modify Phase 8B runtime.

Phase 10B is docs/tests design-only. Actor attribution integration planning is
not runtime integration, audit actor attribution is not authentication, audit
actor attribution is not approval, and approval remains the Phase 7D
selected-gate manual boundary.
