#!/usr/bin/env bash
SOLCJS="/home/claude/reentrancy-lab/node_modules/.bin/solcjs"

if [[ "$1" == "--version" ]]; then
  echo "solc, the solidity compiler commandline interface"
  echo "Version: $($SOLCJS --version)"
  exit 0
fi

args=()
skip_next=0
for arg in "$@"; do
  if [[ $skip_next -eq 1 ]]; then skip_next=0; continue; fi
  case "$arg" in
    --allow-paths) skip_next=1 ;;
    *) args+=("$arg") ;;
  esac
done

# Write to real files (synchronous) instead of piping — piping Node's
# stdout directly into another process can truncate large writes because
# process.exit() can fire before an async pipe write fully flushes.
TMP_OUT=$(mktemp)
TMP_ERR=$(mktemp)
"$SOLCJS" "${args[@]}" >"$TMP_OUT" 2>"$TMP_ERR"
sed -n '/^{/,$p' "$TMP_OUT"
cat "$TMP_ERR" >&2
rm -f "$TMP_OUT" "$TMP_ERR"
