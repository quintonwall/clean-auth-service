#!/usr/bin/env python3

This script runs the Fleet Logistics CI/CD pipleine:
1. Build stage 
2. Deploy stage 
3. Post-deploy API validation using `postman collection run`

Required:
  - Postman CLI installed and available in PATH
  - POSTMAN_API_KEY exported in environment (if your run needs auth)
  - Collection identifier or path

Example:
  python scripts/ci_postman_cd.py \
    --collection "123456-abcde-collection-id" \
    --environment "123456-prod-env-id" \
    --folder "smoke-tests" \
    --verbose
"""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import List


@dataclass
class StageResult:
    name: str
    success: bool
    duration_seconds: float
    details: str = ""


def run_stage(name: str, delay_seconds: int = 1) -> StageResult:
    start = time.time()
    print(f"\n=== [{name}] START ===")
    time.sleep(delay_seconds)
    duration = time.time() - start
    print(f"=== [{name}] PASS ({duration:.2f}s) ===")
    return StageResult(name=name, success=True, duration_seconds=duration)


def run_command(command: List[str], verbose: bool = False) -> subprocess.CompletedProcess:
    if verbose:
        print("\n$ " + " ".join(shlex.quote(part) for part in command))
    return subprocess.run(
        command,
        text=True,
        capture_output=True,
        check=False,
    )


def postman_collection_run(
    collection: str,
    environment: str | None,
    folder: str | None,
    verbose: bool,
) -> StageResult:
    start = time.time()
    stage_name = "Postman Collection Validation"
    print(f"\n=== [{stage_name}] START ===")

    command = ["postman", "collection", "run", collection]
    if environment:
        command.extend(["--environment", environment])
    if folder:
        command.extend(["--folder", folder])
    command.extend(["--reporters", "cli"])

    result = run_command(command, verbose=verbose)

    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)

    duration = time.time() - start
    success = result.returncode == 0
    status = "PASS" if success else "FAIL"
    print(f"=== [{stage_name}] {status} ({duration:.2f}s) ===")

    return StageResult(
        name=stage_name,
        success=success,
        duration_seconds=duration,
        details=f"postman exit code={result.returncode}",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simulate a CD pipeline and run Postman collection tests."
    )
    parser.add_argument(
        "--collection",
        required=True,
        help="Postman collection UID, URL, or local collection file path.",
    )
    parser.add_argument(
        "--environment",
        default=None,
        help="Optional Postman environment UID, URL, or local file path.",
    )
    parser.add_argument(
        "--folder",
        default=None,
        help="Optional folder name in the collection to run (e.g., smoke-tests).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print executed command for debugging.",
    )
    return parser.parse_args()


def ensure_preconditions() -> None:
    if not os.getenv("POSTMAN_API_KEY"):
        print(
            "WARN: POSTMAN_API_KEY is not set. "
            "If your collection requires Postman cloud auth, the run may fail.",
            file=sys.stderr,
        )

    check = run_command(["postman", "--version"])
    if check.returncode != 0:
        print(
            "ERROR: Postman CLI not found. Install it and ensure `postman` is in PATH.",
            file=sys.stderr,
        )
        sys.exit(2)


def print_summary(results: List[StageResult]) -> None:
    print("\n=== PIPELINE SUMMARY ===")
    overall_success = True
    for item in results:
        marker = "PASS" if item.success else "FAIL"
        print(f"- {item.name}: {marker} ({item.duration_seconds:.2f}s) {item.details}")
        overall_success = overall_success and item.success

    if overall_success:
        print("\nCD simulation completed successfully.")
    else:
        print("\nCD simulation failed.")
    sys.exit(0 if overall_success else 1)


def main() -> None:
    args = parse_args()
    ensure_preconditions()

    results: List[StageResult] = []
    results.append(run_stage("Build", delay_seconds=1))
    results.append(run_stage("Deploy to Staging", delay_seconds=1))
    results.append(
        postman_collection_run(
            collection=args.collection,
            environment=args.environment,
            folder=args.folder,
            verbose=args.verbose,
        )
    )
    print_summary(results)


if __name__ == "__main__":
    main()
