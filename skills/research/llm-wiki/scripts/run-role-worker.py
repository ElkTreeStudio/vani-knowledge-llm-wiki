#!/usr/bin/env python3
"""Dispatch an isolated llm-wiki governance role through Hermes oneshot."""

import argparse
import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path


PLANNER_CONTRACT = """ROLE CONTRACT — PROMOTION PLANNER
You are a read-only promotion planner. Do not create, modify, delete, move, or
rename any file. Read only the task packet's allowlisted scope and return only
the promotion-plan schema required by the preloaded llm-wiki skill. Report
uncertainty, conflicts, evidence gaps, and out-of-scope impacts; never resolve
them by writing.
"""

MAINTAINER_CONTRACT = """ROLE CONTRACT — FORMAL MAINTAINER
You are a governed formal-knowledge maintainer. For an explicit
`operation_mode: audit-only` packet, perform only the bounded read-only audit and
return findings plus a proposed plan; do not modify files.

For `operation_mode: formal-write`, act only when the packet includes an
effective promotion plan, an explicitly approved policy gate, exactly one bounded
write allowlist, and stop conditions. Revalidate required inputs before writing.
Stop on expired or stale evidence, missing conditions, collisions, or any
boundary expansion. Never self-approve a plan or broaden an allowlist.
"""

CONTRACTS = {
    "planner": PLANNER_CONTRACT,
    "maintainer": MAINTAINER_CONTRACT,
}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", choices=sorted(CONTRACTS), required=True)
    prompts = parser.add_mutually_exclusive_group(required=True)
    prompts.add_argument("--prompt")
    prompts.add_argument("--prompt-file", type=Path)
    parser.add_argument("--workdir", type=Path, default=Path.cwd())
    parser.add_argument("--usage-file", type=Path)
    parser.add_argument(
        "--model",
        help="Optional model ID resolved by runtime policy; use together with --provider.",
    )
    parser.add_argument(
        "--provider",
        help="Optional provider ID resolved by runtime policy; use together with --model.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def read_prompt(args):
    if args.prompt is not None:
        return args.prompt
    try:
        return args.prompt_file.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError("cannot read --prompt-file: {}".format(exc)) from exc


def validate_runtime_selection(args):
    if bool(args.model) != bool(args.provider):
        raise ValueError("--model and --provider must be supplied together")


def _field_values(prompt, field):
    """Return exact single-line values for `field:` without crossing newlines."""
    pattern = r"^{}:[ \t]*(.*?)[ \t]*$".format(re.escape(field))
    return re.findall(pattern, prompt, flags=re.IGNORECASE | re.MULTILINE)


def _require_single_field(prompt, field, *, nonempty=True):
    values = _field_values(prompt, field)
    if len(values) != 1:
        raise ValueError(
            "task packet must declare exactly one {!r} field".format(field)
        )
    value = values[0].strip()
    if nonempty and not value:
        raise ValueError("task packet field {!r} must not be empty".format(field))
    return value


def _require_operation_mode(prompt, expected):
    value = _require_single_field(prompt, "operation_mode")
    if value.casefold() != expected.casefold():
        raise ValueError(
            "task packet operation_mode must be {!r}, got {!r}".format(expected, value)
        )


def _require_stop_conditions(prompt):
    _require_single_field(prompt, "stop conditions")


def validate_planner_packet(prompt):
    _require_operation_mode(prompt, "promotion-plan")
    _require_single_field(prompt, "read allowlist")
    write_allowlist = _require_single_field(prompt, "write allowlist")
    if write_allowlist.casefold() != "none":
        raise ValueError("planner write allowlist must be exactly 'none'")
    _require_stop_conditions(prompt)


def validate_maintainer_packet(prompt):
    modes = _field_values(prompt, "operation_mode")
    if len(modes) != 1:
        raise ValueError("maintainer packet must declare exactly one operation_mode")
    mode = modes[0].strip().casefold()

    if mode == "audit-only":
        write_allowlist = _require_single_field(prompt, "write allowlist")
        if write_allowlist.casefold() != "none":
            raise ValueError("audit-only maintainer write allowlist must be exactly 'none'")
        _require_stop_conditions(prompt)
        return

    if mode != "formal-write":
        raise ValueError(
            "maintainer packet must declare operation_mode: audit-only or formal-write"
        )

    _require_single_field(prompt, "effective promotion plan")

    policy_gate = _require_single_field(prompt, "policy gate")
    if policy_gate.casefold() != "approved":
        raise ValueError("formal-write policy gate must be exactly 'approved'")

    write_allowlist = _require_single_field(prompt, "write allowlist")
    if write_allowlist.casefold() == "none":
        raise ValueError("formal-write write allowlist must name one bounded target/scope")

    _require_stop_conditions(prompt)


def validate_packet(role, prompt):
    if role == "planner":
        validate_planner_packet(prompt)
    elif role == "maintainer":
        validate_maintainer_packet(prompt)


def default_usage_path():
    hermes_home = Path(
        os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))
    ).expanduser()
    directory = hermes_home / "worker-runs" / "llm-wiki"
    directory.mkdir(parents=True, exist_ok=True)
    return directory / ("worker-{}.json".format(uuid.uuid4().hex))


def load_and_verify_usage(path, expected_model=None, expected_provider=None):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("unable to read usage JSON: {}".format(exc)) from exc

    if data.get("completed") is not True or data.get("failed") is not False:
        raise RuntimeError("usage JSON does not confirm completed=true and failed=false")

    actual_model = data.get("model")
    actual_provider = data.get("provider")
    if not isinstance(actual_model, str) or not actual_model.strip():
        raise RuntimeError("usage JSON does not record a non-empty model identity")
    if not isinstance(actual_provider, str) or not actual_provider.strip():
        raise RuntimeError("usage JSON does not record a non-empty provider identity")

    if expected_model is not None:
        if actual_model != expected_model or actual_provider != expected_provider:
            raise RuntimeError(
                "usage JSON model/provider mismatch: got {!r}/{!r}, expected {!r}/{!r}".format(
                    actual_model,
                    actual_provider,
                    expected_model,
                    expected_provider,
                )
            )

    return data


def build_command(args, worker_prompt, usage_path):
    command = [
        "hermes",
        "--oneshot",
        worker_prompt,
        "--skills",
        "llm-wiki",
        "--usage-file",
        str(usage_path),
    ]
    if args.model:
        command.extend(["--model", args.model, "--provider", args.provider])
    return command


def main():
    args = parse_args()
    try:
        validate_runtime_selection(args)
        prompt = read_prompt(args)
        validate_packet(args.role, prompt)
    except ValueError as exc:
        print("run-role-worker: {}".format(exc), file=sys.stderr)
        return 2

    workdir = args.workdir.expanduser().resolve()
    if not workdir.is_dir():
        print("run-role-worker: --workdir is not a directory: {}".format(workdir), file=sys.stderr)
        return 2

    routing = (
        "explicit {}/{}".format(args.provider, args.model)
        if args.model
        else "runtime-default"
    )
    if args.dry_run:
        print(
            "dry-run role={} routing={} workdir={}".format(
                args.role,
                routing,
                workdir,
            )
        )
        return 0

    try:
        usage_path = (
            args.usage_file.expanduser().resolve()
            if args.usage_file
            else default_usage_path()
        )
        if not args.usage_file:
            print(
                "run-role-worker: default usage file: {}".format(usage_path),
                file=sys.stderr,
            )
    except OSError as exc:
        print("run-role-worker: cannot create default usage path: {}".format(exc), file=sys.stderr)
        return 2

    worker_prompt = CONTRACTS[args.role] + "\nTASK PACKET\n" + prompt
    command = build_command(args, worker_prompt, usage_path)

    try:
        result = subprocess.run(
            command,
            cwd=str(workdir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        print("run-role-worker: unable to start hermes: {}".format(exc), file=sys.stderr)
        return 1

    if result.returncode != 0:
        print("run-role-worker: hermes exited {}".format(result.returncode), file=sys.stderr)
        if result.stderr:
            print(
                result.stderr,
                end="" if result.stderr.endswith("\n") else "\n",
                file=sys.stderr,
            )
        return result.returncode or 1

    try:
        usage = load_and_verify_usage(
            usage_path,
            expected_model=args.model,
            expected_provider=args.provider,
        )
    except RuntimeError as exc:
        print("run-role-worker: {}".format(exc), file=sys.stderr)
        if result.stderr:
            print(
                result.stderr,
                end="" if result.stderr.endswith("\n") else "\n",
                file=sys.stderr,
            )
        return 1

    print(
        "run-role-worker: actual worker identity: {}/{}".format(
            usage["provider"],
            usage["model"],
        ),
        file=sys.stderr,
    )
    sys.stdout.write(result.stdout)
    if result.stderr:
        print(
            result.stderr,
            end="" if result.stderr.endswith("\n") else "\n",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
