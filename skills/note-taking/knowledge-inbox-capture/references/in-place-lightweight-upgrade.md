# In-place upgrade of a lightweight Inbox intake

Use this reference when an existing lightweight material intake must become a complete Inbox capture under Roy's default contract or an explicit full-capture request. It prevents duplicate files and protects the prior intake if the full run stops.

## Preconditions

- The current request is a full Inbox material capture under the default contract, or explicitly authorizes an in-place upgrade/replacement. A generic request to convert provided material into Inbox is sufficient because full capture is the default; only an explicit lightweight request preserves the lightweight file.
- The exact target file is `status: new`, identifies the same material/source (canonical URL when available, otherwise the stable material identity), and is recognizably a lightweight intake (minimum metadata plus date/source identification and a pending-full-capture note).
- The target is not in a no-touch subtree, and the backup directory is outside `${KNOWLEDGE_ROOT}/`.

If the current request explicitly asks to keep only a lightweight intake, do not upgrade. Otherwise, a generic request to convert/provide material to Inbox follows the default full-capture contract and is sufficient to proceed. If any other precondition fails, stop and ask; do not infer permission to touch a different file or broaden the allowlist.

## Safe sequence

1. Read only the exact target file needed to prove the upgrade precondition. Do not recursively list or search the Inbox.
2. Choose a unique rollback path such as:

   ```text
   ${HERMES_AUDIT_ROOT}/knowledge-inbox/<slug>-lightweight-rollback.md
   ```

3. Confirm the rollback path is absent, then move the existing target there. Confirm the target path is absent and the rollback file is present before creating the packet.
4. Build the Stage A packet with the same final target as its only `write allowlist`. State that the upgrade is user-authorized, and explicitly exclude the rollback file from worker reads. Never use a `-full`, `-v2`, or alternate Inbox filename.
5. Run the selected Stage A executor according to the active-main-brain / `GPT-5.6-luna max` rule. The same executor must acquire, render, translate, summarize, assemble, and write the artifact; no Terra fallback is permitted. The executor may stop if the source or output contract cannot be completed; do not weaken the packet to force a partial result.
6. Validate all of the following from the parent session: usage model/provider, `completed`/`failed`, artifact existence, YAML, fixed sections, rendered block count, exact `## 原文` comparison, translation coverage, summary, and insights.
7. On any stop, blocker, absent artifact, or failed validation, restore the rollback file to the original target path. Report the full upgrade as incomplete.
8. Only after every validation passes, remove the rollback file and temporary packet. Keep the usage audit outside knowledge.

## Failure pattern to treat as a blocker

A structured X Article may be technically retrievable but still be too large for one selected Stage A executor to process and verify completely (for example, hundreds of blocks and tens of thousands of characters). A green usage report does not override this: `completed: true` and `failed: false` indicate runtime completion, not a valid capture. Preserve the original lightweight intake and report the blocker rather than writing a partial capture.

## Do not

- Do not create a second file for the same material/source identity.
- Do not delete the only copy before a rollback exists.
- Do not let the selected Stage A executor read or modify the rollback, packet, usage report, README, Frozen ZIP, or protected subdirectories.
- Do not delete the rollback merely because the selected executor exited successfully; validate the actual artifact first.
- Do not call a lightweight intake a full capture until the original and every required translation block have been verified.
