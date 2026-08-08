#!/usr/bin/env python3
"""Dispatch an isolated, role-bound llm-wiki worker through Hermes oneshot."""

import argparse
import json
import re
import subprocess
import sys
import uuid
from pathlib import Path

ROLE_MODELS = {
    "luna": ("gpt-5.6-luna", "openai-codex"),
    "terra": ("gpt-5.6-terra", "openai-codex"),
    "sol": ("gpt-5.6-sol", "openai-codex"),
}

LUNA_CONTRACT = """ROLE CONTRACT — LUNA (READ-ONLY PLANNER)
You are Luna. You are strictly read-only: do not create, modify, delete, move,
or rename any file. Return ONLY the Stage B fixed YAML schema defined by the
preloaded llm-wiki skill. Do not add prose, Markdown fences, or any fields
outside that schema. Report uncertainty, conflicts, evidence gaps, and
out-of-domain impacts in the schema; never resolve them by writing.
"""

TERRA_CONTRACT = """ROLE CONTRACT — TERRA (INBOX PRODUCER)
You are Terra. You may perform Stage A intake only: create exactly one Inbox
artifact under the supplied task packet and do not modify formal-library files.
If the requested work is knowledge merge, conflict resolution, wiki/graph/index
update, or any other formal-library write, stop and report that it requires a
high-capability knowledge operator. Never self-approve a plan, broaden an
allowlist, or convert an Inbox artifact directly into formal knowledge.
"""

SOL_CONTRACT = """ROLE CONTRACT — HIGH-CAPABILITY KNOWLEDGE OPERATOR
You are the GPT-5.6-Sol high-capability knowledge operator. For an explicit
`operation_mode: audit-only` task packet, conduct only the bounded read-only
governance audit and return findings plus a proposed plan; do not create,
modify, delete, move, or rename any file. Audit-only work needs no Luna plan or
write gate because it performs no formal-library write.

For Knowledge Merge, Conflict Resolution, Update Wiki, Update Knowledge Graph,
Update Index, or any other formal-library write, act only when the task packet
includes an effective Luna plan, an applicable current-main-brain/Roy gate, a
bounded write allowlist, and stop conditions. Revalidate all required inputs
immediately before every write; stop on an expired plan, stale hash, missing
condition, or boundary expansion. Never self-approve a plan or broaden its
allowlist.
"""

CONTRACTS = {"luna": LUNA_CONTRACT, "terra": TERRA_CONTRACT, "sol": SOL_CONTRACT}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", choices=sorted(ROLE_MODELS), required=True)
    prompts = parser.add_mutually_exclusive_group(required=True)
    prompts.add_argument("--prompt")
    prompts.add_argument("--prompt-file", type=Path)
    parser.add_argument("--workdir", type=Path, default=Path.cwd())
    parser.add_argument("--usage-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def read_prompt(args):
    if args.prompt is not None:
        return args.prompt
    try:
        return args.prompt_file.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError("cannot read --prompt-file: {}".format(exc)) from exc


def validate_terra_packet(prompt):
    required = {
        "Stage A": r"\bstage\s*a\b",
        "Inbox boundary": r"\binbox\b",
        "write allowlist": r"write allowlist",
        "stop conditions": r"\bstop\s+conditions?\b",
    }
    missing = [label for label, pattern in required.items()
               if not re.search(pattern, prompt, flags=re.IGNORECASE)]
    if missing:
        raise ValueError("Terra task packet missing " + ", ".join(missing))

    router_results = re.findall(r"^intent_router_result:\s*(\S+)\s*$", prompt,
                                flags=re.MULTILINE)
    permitted_router_results = {
        "stage-a-inbox-only",
        "stage-a-inbox-only-lightweight",
    }
    if len(router_results) != 1 or router_results[0] not in permitted_router_results:
        raise ValueError(
            "Terra task packet must declare exactly one permitted intent_router_result"
        )

    declarations = re.findall(r"^write allowlist:\s*(\S+)\s*$", prompt,
                              flags=re.MULTILINE)
    if len(declarations) != 1:
        raise ValueError("Terra task packet must declare exactly one write allowlist path")
    allowed_path = Path(declarations[0])
    inbox_root = Path("${KNOWLEDGE_ROOT}/inbox")
    if (not allowed_path.is_absolute() or allowed_path.parent != inbox_root
            or allowed_path.suffix != ".md" or allowed_path.exists()):
        raise ValueError(
            "Terra write allowlist must be one new absolute .md path directly under "
            "${KNOWLEDGE_ROOT}/inbox/"
        )


def validate_high_capability_packet(prompt):
    audit_only = re.search(
        r"^operation_mode:\s*audit-only\s*$", prompt, flags=re.MULTILINE | re.IGNORECASE
    )
    if audit_only:
        required = {
            "write allowlist": r"^write allowlist:\s*none\s*$",
            "stop conditions": r"\bstop\s+conditions?\b",
        }
        missing = [label for label, pattern in required.items()
                   if not re.search(pattern, prompt, flags=re.IGNORECASE | re.MULTILINE)]
        if missing:
            raise ValueError("audit-only high-capability task packet missing " + ", ".join(missing))
        return

    required = {
        "effective Luna plan": r"\bluna\s+plan\b",
        "policy gate": r"\b(?:current.main.brain|roy)\s+gate\b",
        "write allowlist": r"\b(?:write\s+)?allowlist\b",
        "stop conditions": r"\bstop\s+conditions?\b",
    }
    missing = [label for label, pattern in required.items()
               if not re.search(pattern, prompt, flags=re.IGNORECASE)]
    if missing:
        raise ValueError("high-capability task packet missing " + ", ".join(missing))


def default_usage_path(workdir):
    del workdir  # Worker audit artifacts must not pollute the knowledge root.
    directory = Path.home() / ".hermes" / "worker-runs" / "llm-wiki"
    directory.mkdir(parents=True, exist_ok=True)
    return directory / ("worker-{}.json".format(uuid.uuid4().hex))


def load_and_verify_usage(path, expected_model, expected_provider):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("unable to read usage JSON: {}".format(exc)) from exc

    if data.get("completed") is not True or data.get("failed") is not False:
        raise RuntimeError("usage JSON does not confirm completed=true and failed=false")
    if data.get("model") != expected_model or data.get("provider") != expected_provider:
        raise RuntimeError(
            "usage JSON model/provider mismatch: got {!r}/{!r}, expected {!r}/{!r}".format(
                data.get("model"), data.get("provider"), expected_model, expected_provider
            )
        )


def main():
    args = parse_args()
    try:
        prompt = read_prompt(args)
        if args.role == "terra":
            validate_terra_packet(prompt)
        elif args.role == "sol":
            validate_high_capability_packet(prompt)
    except ValueError as exc:
        print("run-role-worker: {}".format(exc), file=sys.stderr)
        return 2

    workdir = args.workdir.expanduser().resolve()
    if not workdir.is_dir():
        print("run-role-worker: --workdir is not a directory: {}".format(workdir), file=sys.stderr)
        return 2

    model, provider = ROLE_MODELS[args.role]
    if args.dry_run:
        print("dry-run role={} model={} provider={} workdir={}".format(
            args.role, model, provider, workdir
        ))
        return 0

    try:
        usage_path = (args.usage_file.expanduser().resolve()
                      if args.usage_file else default_usage_path(workdir))
        if not args.usage_file:
            print("run-role-worker: default usage file: {}".format(usage_path), file=sys.stderr)
    except OSError as exc:
        print("run-role-worker: cannot create default usage path: {}".format(exc), file=sys.stderr)
        return 2

    worker_prompt = CONTRACTS[args.role] + "\nTASK PACKET\n" + prompt
    command = [
        "hermes", "--oneshot", worker_prompt,
        "--model", model,
        "--provider", provider,
        "--skills", "llm-wiki",
        "--usage-file", str(usage_path),
    ]
    try:
        result = subprocess.run(
            command, cwd=str(workdir), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace", check=False,
        )
    except OSError as exc:
        print("run-role-worker: unable to start hermes: {}".format(exc), file=sys.stderr)
        return 1

    if result.returncode != 0:
        print("run-role-worker: hermes exited {}".format(result.returncode), file=sys.stderr)
        if result.stderr:
            print(result.stderr, end="" if result.stderr.endswith("\n") else "\n", file=sys.stderr)
        return result.returncode or 1

    try:
        load_and_verify_usage(usage_path, model, provider)
    except RuntimeError as exc:
        print("run-role-worker: {}".format(exc), file=sys.stderr)
        if result.stderr:
            print(result.stderr, end="" if result.stderr.endswith("\n") else "\n", file=sys.stderr)
        return 1

    sys.stdout.write(result.stdout)
    if result.stderr:
        print(result.stderr, end="" if result.stderr.endswith("\n") else "\n", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
