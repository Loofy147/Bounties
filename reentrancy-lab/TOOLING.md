# Equipment: getting Slither working without network access to binaries.soliditylang.org

On a normal machine, skip all of this: `pip install slither-analyzer solc-select && solc-select install 0.8.19 && solc-select use 0.8.19` just works, because solc-select fetches native binaries from the internet.

This lab was built in a sandbox that can reach npm/PyPI/GitHub but **not** `binaries.soliditylang.org`, so `solc-select install` fails. The fix, documented here because it's a genuinely useful trick for any locked-down CI/audit environment:

1. `npm install solc` — the npm package ships the compiler as pure JS/WASM, no extra network call needed.
2. `npm install -g solc` gives you `solcjs`, a CLI that supports `--standard-json` (just not the same flags as native `solc`).
3. Write a shell shim at `/usr/local/bin/solc` that:
   - answers `--version` in native solc's expected format (`Solc-select`/`crytic-compile` parse this)
   - strips `--allow-paths` (a native-only flag `solcjs` doesn't recognize)
   - **redirects solcjs's stdout to a real file, not a live pipe** — this was the actual bug that cost the most time. Node truncates large stdout writes when piped directly into another process and `process.exit()` fires before the async pipe write flushes. Writing to a file first (synchronous on POSIX) and then `cat`-ing it avoids the truncation entirely.
   - strips a stray `>>> Cannot retry compilation with SMT...` warning line solcjs prints to stdout before the JSON, which breaks JSON parsing downstream.
4. Force Slither onto the standard-json compile path (`--compile-force-framework solc-json`) and hand it a **standard-json INPUT file** (not a `.sol` file — that's a different platform in `crytic-compile` with a similar name and this cost real debugging time too). `to_standard_json.js` in this repo builds that input file from any `.sol` source.

Result: `./run_slither.sh contracts/whatever.sol` — real Slither, real detectors, zero native binary downloads.

## Full commands
```bash
pip install slither-analyzer solc-select --break-system-packages
npm install solc ganache ethers@5
# then install the /usr/local/bin/solc wrapper (see repo, or reconstruct from above)
./run_slither.sh contracts/VulnerableVault.sol
```
