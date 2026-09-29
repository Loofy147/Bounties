#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-}"

if [[ -z "$TARGET_DIR" ]]; then
  echo "usage: $0 /path/to/limit-order-protocol-4.3.2" >&2
  exit 2
fi

if [[ ! -d "$TARGET_DIR/.git" ]]; then
  echo "ERROR: target directory is not a git repository: $TARGET_DIR" >&2
  exit 2
fi

cd "$TARGET_DIR"

EXPECTED_COMMIT="67c56aee3b6a9f4982bf487084bd8da1f6638da0"
ACTUAL_COMMIT="$(git rev-parse HEAD)"

echo "target_commit=$ACTUAL_COMMIT"
if [[ "$ACTUAL_COMMIT" != "$EXPECTED_COMMIT" ]]; then
  echo "ERROR: refusing to run against an unpinned target." >&2
  echo "expected=$EXPECTED_COMMIT" >&2
  echo "actual=$ACTUAL_COMMIT" >&2
  exit 3
fi

echo "node_version=$(node --version)"
echo "yarn_version=$(yarn --version)"
echo "lockfile_sha256=$(sha256sum yarn.lock | awk '{print $1}')"
echo "working_tree=$(git status --porcelain)"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "ERROR: refusing to run with a dirty target tree." >&2
  exit 4
fi

echo "RUN: yarn test:ci"
exec yarn test:ci
