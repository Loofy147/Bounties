# Smart Contract Security Lab — Field Manual (v2, 9 modules)

Nine vulnerability classes. Each one: a real contract, a real exploit, real measured numbers from actually running it, a Slither run to show what tooling does and doesn't catch, and a real incident (mostly 2026) it's not a toy version of.

## Run any module
```bash
npm install
node exploit.js       # M1 - reentrancy
node exploit_m2.js    # M2 - access control
node exploit_m3.js    # M3 - oracle manipulation
node exploit_m4.js    # M4 - vault inflation
node exploit_m5.js    # M5 - signature replay
node exploit_m6.js    # M6 - cross-chain domain separation
node exploit_m7.js    # M7 - uninitialized proxy
node exploit_m8.js    # M8 - flash-loan governance attack
node exploit_m9.js    # M9 - MEV sandwich (missing slippage protection)
./run_slither.sh contracts/<path>.sol            # static analysis on any module
python3 detect_missing_domain_binding.py contracts/<path>.sol   # custom detector for unbound signatures
```
See TOOLING.md for how the Slither pipeline works fully offline, OPSEC.md for the loss category this lab deliberately doesn't cover, BYTECODE.md for the one gap left genuinely open.

## inspector.py — point this at a contract you've never seen before

Everything above is nine worked examples. `inspector.py` is the actual reusable tool that came out of building them: stock Slither (all 102 detectors, triaged to cut noise) plus five custom detectors, each one mechanically distilled from a pattern this lab proved Slither misses.

```bash
python3 inspector.py path/to/any_contract.sol
```

| Custom check | Built from | Catches |
|---|---|---|
| `unbound-signature` | M5, M6 | `ecrecover()` with no `block.chainid`/`address(this)` bound into the signed message |
| `unprotected-initializer` | M2, M7 | an `init*`-named function that sets a privileged variable with no `msg.sender` check anywhere in it |
| `raw-balance-valuation` | M4 | a price/rate/`totalAssets`-style function reading `balanceOf(address(this))` directly |
| `live-balance-voting` | M8 | voting power pulled from live `balanceOf(msg.sender)`, no snapshot/checkpoint anywhere in the contract |
| `unbounded-swap` | M9 | a swap/trade/exchange function with no min-output or slippage parameter |

Validated by running it against all nine of this lab's own modules: 8 of 9 got a precise custom-detector hit (M1's reentrancy was already well-covered by stock Slither — no custom check needed), zero false positives, and one honest bonus catch — `unbounded-swap` also correctly flagged M3's AMM, and correctly stayed silent on M9's *protected* swap variant once it had a `minTokenOut` parameter.

**Stated limitation, not hidden**: M3's class — spot-price manipulation via an AMM with no TWAP — isn't auto-detected. It's a structural absence ("there's no historical price tracking anywhere in this contract"), not a text pattern, and doesn't reduce to a cheap heuristic without real dataflow analysis. Five out of six non-reentrancy classes closing with custom tooling, one still requiring a human, is an honest result worth stating plainly rather than papering over.

## The nine modules

| # | Bug | Measured result | Slither catches it? | Real-world incident, same shape |
|---|---|---|---|---|
| 1 | External call before state update (reentrancy) | 15 ETH pool to 6 ETH; attacker nets ~8 ETH on a 1 ETH stake | Yes - exact line, exact call | Solv Protocol, Jan 2026, $2.7M |
| 2 | initialize() has no access guard | 75 ETH drained, zero capital | Partial - flags a zero-address nit, misses the real authz hole | Parity 2017 (the archetype) |
| 3 | Lending pool trusts a no-TWAP AMM spot price | Flash-borrowed 100 ETH, price pumped 36x, borrowed 300 ETH on fake collateral, ~200 ETH profit from zero capital | No | Makina Finance $5.1M, YieldBlox $10.2M, Drift Protocol $285M - all 2026 |
| 4 | Vault share price uses raw balanceOf, donation-manipulable | Victim deposits 5,000 tokens, gets 0 shares, loses everything | No | Generic "ERC4626 inflation attack"; Edel Finance 2026 ($403K, 78x, via a wrapper-conversion variant of this same idea) |
| 5 | Signed withdrawal voucher has no nonce/used-tracking | One 1 ETH voucher, replayed 20x, drains a 20 ETH pool | No | Classic signature-replay class |
| 6 | Bridge signs (depositId, recipient, amount) - no chain id/contract address bound in | One real 1000-token deposit minted TWICE across two chain deployments sharing a relayer | No - bug only exists between deployments | KelpDAO, Apr 2026, $292M - LayerZero, single-verifier config shared by 1,200+ OApp contracts |
| 7 | Naked implementation contract behind a proxy is independently callable and initializable | Attacker hijacks the shared implementation directly; selfdestruct bricks a dependent proxy | Partial - flags unrelated nits, misses the composed authz+selfdestruct path | Immunefi's own highest-ever paid bounty: Wormhole, $10M. Also literally the 2017 Parity mechanism. |
| 8 | Governance uses live token balance for voting power, no timelock before execution | Propose -> flash-borrow 600K votes -> vote -> execute -> repay, ONE transaction; 2,000,000-token treasury drained to zero | No | Beanstalk Farms, 2022, $182M (the archetype); Drift Protocol 2026 combined this pattern with oracle abuse |
| 9 | Swap function has no minimum-output / slippage parameter | Victim swaps 5 ETH, gets 2,381 tokens instead of a fair 4,545 - attacker nets ~22.5 ETH from one ordinary trade | No | Generic MEV sandwich; the single most common form of value extraction on public mempools |

Bonus finding, not a planned module: building M7's proxy naively (implementation address stored as a normal state variable at slot 0) collided with Implementation's own `bool initialized` at the same slot, corrupting every initialize() call before the intended bug was even reachable. Fixed with the real EIP-1967 unstructured-storage pattern. Left in the contract's comments because it's a second real, common vulnerability class discovered by accident, not a contrived example.

The pattern across M3, M4, M5, M6, M8, M9: static analysis is real equipment, not a substitute for reasoning about trust assumptions. It's excellent at syntactic patterns and consistently blind to "is this economic design sound," "does this signed message mean the same thing in every context it's checked in," and "can voting power/collateral value/output amount be manipulated within the transaction that uses it."

## Where the money actually went in 2026

- **The inversion**: compromised private keys and infrastructure overtook smart contract bugs as DeFi's #1 loss vector for the first time on record, through August 2026 - $1.3B across eight months. See OPSEC.md; nothing in this lab's contract-level training touches that category.
- **Oracle manipulation and cross-chain messaging remain the top *code-level* loss categories** - M3, M6, and M8 (Drift's case combined governance with oracle abuse) are all built around live 2026 nine-figure incidents.
- **KelpDAO's $292M wasn't an exotic bug.** A bridge configured with a single verifier - 1,200+ other LayerZero OApp contracts shared that exact configuration. A design choice made at scale, exactly what M7 and M6 both train you to ask about.
- **AI is on both sides.** A Feb 2026 benchmark (Cecuro) found a purpose-built AI security agent independently detected 92% of the vulnerabilities behind $228M in real losses. Separately, reported AI exploit-generation capability has been doubling roughly every 1.3 months at ~$1.22/contract. The pattern-matchable bugs here (M1, M2, M5, M7) are exactly what that automates fastest. The economic-reasoning bugs (M3, M4, M6, M8, M9) stay hard for automation and valuable for a human who understands the trust model - which is also exactly why this lab weights toward building custom detectors (see detect_missing_domain_binding.py) instead of trusting only stock tooling.

## Immunefi, as it actually works right now

- **VSCS v2.3** - 5 severity levels (Critical/High/Medium/Low/None), scored on impact/privilege/likelihood, not cleverness.
- **Primacy of Impact** - a real in-scope impact reached via a technically-out-of-scope asset still pays at the real severity.
- **~92% of publicly disclosed critical crypto vulnerabilities go through Immunefi** - close to the whole market for this kind of disclosure.
- **Know what it doesn't cover well**: strongest for on-chain smart-contract state bugs (everything M1-M9 train for), structurally weaker for the private-key/opsec category that's now the biggest single loss driver in 2026. Read OPSEC.md before assuming a clean audit means a protocol is safe.

## Workflow, for real targets
1. Static pass: Slither + Mythril. Cheap, fast, catches pattern-matchable stuff - expect silence on M3/M4/M6/M8/M9-shaped bugs.
2. Write a custom detector for whatever trust-boundary question you keep re-checking by hand (see detect_missing_domain_binding.py for the template).
3. Dynamic/fuzz pass: Foundry fuzzing or Echidna invariants for the economic-logic bugs static tools miss.
4. Manual review, trust-boundary framing: for every signed message, oracle read, governance vote, and swap - what does this assume about caller/context/timing, and is that assumption enforced anywhere?
5. Fork mainnet locally (Foundry --fork-url), never touch the live contract. That's the PoC.
6. Report through Immunefi, severity argued against VSCS v2.3, not against how impressive the finding feels.
7. Separately, ask the OPSEC.md questions about the *protocol*, not just its contracts - a perfect audit doesn't help if the treasury key sits in an unmonitored KMS role.

---

Bonus, still on the house: keccak256(abi.encodePacked("still no espresso machine in /home/claude")). Nine modules deep and still fully caffeinated in spirit only.

## Sources
- KelpDAO / LayerZero single-verifier analysis, 1,200+ OApp figure - immunefi.com/blog/research, crypto.news Q1-Q3 2026 coverage
- Private-key-overtakes-contract-bugs inversion, $1.3B/8-months figure - crypto.news, Sept 2026
- Cecuro AI detection benchmark; AI exploit-generation capability trend - coindesk.com, Feb 2026
- Immunefi VSCS v2.3, Primacy of Impact, 92% disclosure share - immunefi.com
- Per-incident figures (Makina, YieldBlox, Solv, Edel Finance, Bonzo, Step Finance, Resolv Labs) - ccn.com, phemex.com, kucoin.com 2026 hack trackers
- Beanstalk Farms governance attack - public post-mortems, 2022
