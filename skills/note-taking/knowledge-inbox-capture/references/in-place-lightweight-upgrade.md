# In-place upgrade of a lightweight Inbox intake

Use this reference when an existing lightweight material intake must become a complete Inbox capture under the default contract or an explicit full-capture request. It prevents duplicate files and protects the prior intake if the full run stops.

## Preconditions

- The current request is a full Inbox material capture under the default contract, or explicitly authorizes an in-place upgrade/replacement. A generic request to convert provided material into Inbox is sufficient because full capture is the default; only an explicit lightweight request preserves the lightweight file.
- The exact target file is `status: new`, identifies the same material/source (canonical URL when available, otherwise the stable material identity), and is recognizably a lightweight intake (minimum metadata plus date/source identification and a pending-full-capture note).
- The target is not the Frozen ZIP, README, or another current live-contract exclusion, and the backup directory is outside `${KNOWLEDGE_ROOT}/`.

If the current request explicitly asks to keep only a lightweight intake, do not upgrade. Otherwise, a generic request to convert/provide material to Inbox follows the default full-capture contract and is sufficient to proceed. If any other precondition fails, stop and ask; do not infer permission to touch a different file or broaden the allowlist.

## Safe sequence

1. Read only the exact target file needed to prove the upgrade precondition. Do not recursively list or search the Inbox.
2. Before moving the existing target, run `scripts/validate_inbox_target.py --mode in-place-upgrade` with the resolved knowledge root and exact target. This must pass before the target can be used as an upgrade destination.
3. Choose a unique rollback path such as:

   ```text
   ${HERMES_AUDIT_ROOT}/knowledge-inbox/<slug>-lightweight-rollback.md
   ```

4. Confirm the rollback path is absent, then move the existing target there. Confirm the target path is absent and the rollback file is present before creating the packet.
5. Build the capture packet with the same final target as its only `write allowlist`. Use the resolved absolute Inbox path for machine validation. State that the upgrade is user-authorized, and explicitly exclude the rollback file from executor reads. Never use a `-full`, `-v2`, or alternate Inbox filename.
6. Run the selected capture executor according to current runtime policy and the capability contract in `knowledge-inbox-capture`. The same selected executor must acquire, render, translate, summarize, assemble, and write the artifact; do not silently substitute another executor after a failure. The executor may stop if the source or output contract cannot be completed; do not weaken the packet to force a partial result.
7. Validate all of the following from the parent session: delegated runtime identity/completion evidence when applicable, artifact existence, YAML, fixed sections, rendered block count, exact `## 原文` comparison, translation coverage, summary, and insights.
8. On any stop, blocker, absent artifact, or failed validation, restore the rollback file to the original target path. Report the full upgrade as incomplete.
9. Only after every validation passes, remove the rollback file and temporary packet. Keep delegated-worker usage audit outside knowledge.

## Failure pattern to treat as a blocker

A structured X Article may be technically retrievable but still be too large for the selected capture execution path to process and verify completely (for example, hundreds of blocks and tens of thousands of characters). A green usage report does not override this: `completed: true` and `failed: false` indicate runtime completion, not a valid capture. Preserve the original lightweight intake and report the blocker rather than writing a partial capture.

## Do not

- Do not create a second file for the same material/source identity.
- Do not delete the only copy before a rollback exists.
- Do not let the selected capture executor read or modify the rollback, packet, usage report, README, Frozen ZIP, or any other current live-contract exclusion.
- Do not delete the rollback merely because the selected executor exited successfully; validate the actual artifact first.
- Do not call a lightweight intake a full capture until the original and every required translation block have been verified.
