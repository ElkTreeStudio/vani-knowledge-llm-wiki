# Independent Verifier Normalization

This reference captures the reusable post-commit verifier pattern: normalize full POSIX modes and permission-only modes before comparison; apply the frozen `.DS_Store`/README marker policy before metadata access and exclude markers from content path sets; derive expected paths from exact baseline delta plus explicitly listed run evidence; and keep `producer_committed` distinct from `accepted` until a corrected read-only verifier passes and validation is read back.

## Canonical mode

Parse octal evidence and compare `stat.S_IFMT(mode) | stat.S_IMODE(mode)` on both sides. Do not compare raw `0o100600` and `0o600` strings.

## Marker policy

Decide exact lexical paths or marker basenames before `lstat`, open, hash, parse, or recursion. Skip excluded markers from content expected-path comparison and report their count separately. Never turn pre-existing control markers into unexpected deltas.

## Expected path set

`(baseline - exact source removals) + exact payloads + exact sidecars + exact staging + explicitly listed run-evidence files`. A changed maintenance log is a replacement of an existing path, not a new path.

## Acceptance sequence

Run the verifier read-only, repair representation/schema normalization rather than content when failures are verifier defects, then update validation to `independent_acceptance: accepted` only after a clean PASS and read-back. Preserve the producer terminal state in the run evidence. If no worker is active, state that plainly.
