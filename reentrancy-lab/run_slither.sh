#!/usr/bin/env bash
# Usage: ./run_slither.sh contracts/SomeContract.sol
set -e
TARGET="$1"
DIR="$(dirname "$TARGET")"
node to_standard_json.js "$TARGET"
JSON="${TARGET%.sol}.input.json"
slither "$JSON" --compile-force-framework solc-json --solc-working-dir "$DIR"
