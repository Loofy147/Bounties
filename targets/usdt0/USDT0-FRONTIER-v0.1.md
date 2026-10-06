# USDT0 / IOTA Lockbox Frontier v0.1

Captured: 2026-10-06
Repository: `Loofy147/Bounties`
Branch: `research/usdt0-lab-frontier-v0.1`
PR: #22 (draft)
Primary target: Ethereum OApp Adapter (IOTA) / IOTA Lockbox
Target address: `0xAEf027F94008430BF4Fc27FFABB49ea6F1dd3414`

## Frontier status

| Claim | Status | Evidence / decision |
|---|---|---|
| Target is in current USDT0 scope | ESTABLISHED | USDT0 deployment + Immunefi scope revision 2026-09-30 |
| Target address is the Ethereum IOTA Lockbox | ESTABLISHED | Official USDT0 deployment docs |
| Route is Ethereum <-> IOTA only | ESTABLISHED | Official USDT0 deployment + technical docs |
| Ethereum LZ EID is 30101 | ESTABLISHED | Official USDT0 deployment docs |
| IOTA LZ EID is 30423 | ESTABLISHED | Official USDT0 deployment docs |
| Proxy is EIP-1967 TransparentUpgradeableProxy | ESTABLISHED | Sourcify exact_match of proxy source; live linkage bundle still uses secondary deployment evidence |
| Current implementation is `0x1ab288f49e18884b3a5358f4079ca0f40b891d99` | ESTABLISHED | Dedaub live-RPC linkage + Sourcify exact_match; repository commit UNKNOWN |
| Endpoint is `0x1a44076050125825900e736c501f859c50fE728c` | ESTABLISHED | Secondary live-RPC reference |
| Current IOTA peer value | ESTABLISHED | Alchemy eth_call at pinned block 25,989,160 returns the official IOTA OFT peer package `0xe6a11eb6...60b5902` |
| Documented DVN policy | ESTABLISHED | USDT0 docs specify 3/3: LayerZero Labs + USDT0 + Canary; target has an app-specific 3/3 override with 1500 confirmations; third provider identity remains UNKNOWN |
| Exact audit coverage for current implementation | UNKNOWN | Historical reports do not yet establish exact code correspondence |
| Current vulnerability | NONE_CLAIMED | No target-level exploit has been established |

## Evidence hierarchy

1. **Primary target/program authority**
   - Immunefi scope
   - USDT0 deployment and technical documentation
2. **Primary protocol implementation**
   - LayerZero V2 source code at an identified revision
3. **Live deployment observation**
   - block-pinned RPC/fork observations
4. **Secondary verification**
   - Dedaub and other independent deployment references
5. **Historical audit material**
   - Paladin, OpenZeppelin, Guardian
6. **Research claims**
   - public GitHub issues, community reports, unvalidated bounty submissions

Repetition never upgrades a lower-level source into a higher-level evidence class.

## Current correspondence chain

```
USDT0 scope
  -> official deployment address
  -> proxy
  -> implementation
  -> exact bytecode/source
  -> repository commit
  -> LayerZero library/config revision
  -> applicable audit scope
```

The remaining provenance gaps are:

```
implementation address
  -> exact source/commit       UNKNOWN
  -> applicable audit version  UNKNOWN
third required DVN address
  -> independent provider identity UNKNOWN
```

The current peer and app-specific receive ULN override are no longer unknown.

## Lab state

### LayerZero V2 boundary benchmark

Artifact:
`reentrancy-lab/LAYERZERO-V2.md`

Status: OPEN / UNVERIFIED

Modelled invariants:
- only configured Endpoint may enter the OApp receiver boundary;
- Origin peer must match the configured peer for the source EID;
- the modeled channel rejects duplicate packet effects.

Controlled mutants:
- missing Endpoint gate;
- missing Peer gate;
- missing replay guard.

No authoritative CI run has been observed for PR #22, so the benchmark is not marked EXPERIMENTALLY_SUPPORTED.

### Effective configuration resolver

Artifact:
`reentrancy-lab/tools/layerzero_effective_config.py`

Status: OPEN / UNVERIFIED

Purpose:
- prevent the false inference `empty app config == zero DVNs`;
- resolve application override versus default receive-library inheritance;
- retain provenance and unresolved state;
- separate current-state resolution from historical reconstruction.

The resolver is deterministic and has regression fixtures, but an authoritative CI execution is still missing.

## New architectural constraint

LayerZero configuration is not one flat object.

At minimum, preserve separate evidence domains:

```
A. receive path
   OApp receive-library selection
   -> ReceiveUln configuration
   -> DVN quorum / confirmations

B. send path
   OApp send-library selection
   -> SendUln configuration
   -> Executor configuration / send-side ULN

C. application boundary
   Endpoint caller
   -> Origin.srcEid
   -> Origin.sender / peer
   -> nonce / GUID / payload

D. deployment authority
   proxy / implementation / owner / delegate
   -> upgrade and configuration mutation rights
```

Do not merge send-side Executor configuration into a claim about the receive-side DVN quorum.

## Discriminating experiments

### E0 — CI execution gate

Run:
- LayerZero V2 boundary benchmark
- effective configuration resolver regression

Acceptance:
- all expected positive/negative benchmark assertions pass;
- resolver explicit/inherited/unresolved fixtures pass.

Failure action:
- keep status OPEN / UNVERIFIED and repair the lab before target analysis.

### E1 — Exact implementation correspondence

Input:
- target implementation bytecode from a permitted fork;
- candidate USDT0 repository revisions.

Output:
- exact bytecode match or deterministic mismatch;
- source commit if verified.

Kill condition:
- no exact correspondence -> no claim based on a historical implementation review.

### E2 — Peer/config snapshot

Direct state is now pinned at block 25,989,160 via Alchemy. Local-fork reproduction remains OPEN.

Collect:
- `peers(30423)` from the Ethereum lockbox;
- effective receive library for source EID 30423;
- ReceiveUln ULN config;
- send-library / Executor config separately.

Record:
- chain ID;
- LZ EID;
- block number;
- RPC provenance;
- target code hash;
- decoded values.

### E3 — Historical configuration reconstruction

Reconstruct only the events required to explain state transitions:
- `PeerSet`;
- `ReceiveLibrarySet`;
- `DefaultReceiveLibrarySet`;
- `ReceiveLibraryTimeoutSet`;
- receive-side `UlnConfigSet`;
- default receive-library / ULN changes where emitted by the deployed protocol version.

Each event record must preserve:
- transaction hash;
- block number;
- block hash;
- emitter;
- event signature/topic;
- decoded parameters;
- source ABI/revision;
- observation timestamp.

Kill condition:
- incomplete event history -> status UNKNOWN, not an inferred configuration.

### E4 — Lock/mint accounting invariant

On a permitted local fork, establish a small state machine:

```
Ethereum lock -> IOTA mint
IOTA burn     -> Ethereum unlock
```

Required properties:
- no unlock without an authorized source-side state;
- no duplicate economic effect from the same authenticated message;
- amount conversion stays within documented dust semantics;
- `minAmountLD` is enforced on the source-side debit path; it is not a destination receive-path parameter.

This is the first target-specific semantic lane; no live mainnet testing.

### E5 — Known-issue / audit gate

For every candidate:
1. exact implementation/source correspondence;
2. audited scope correspondence;
3. historical finding status;
4. current deployment/version delta;
5. novelty after the above.

A historical finding cannot be reused merely because the contract family has the same name.

## Negative / killed work retained

- Generic signature-replay reasoning from M6 is **not** a LayerZero V2 target model.
- Empty LayerZero ULN config is **not** treated as a zero-DVN security failure.
- Public USDT0 issue #4 is **not** treated as a validated vulnerability.
- Historical Paladin initializer finding is **not** treated as a current regression without code correspondence.
- No live target probing is performed.

## Decision frontier

Current decision: **RESEARCH CONTINUES**

The highest-value next artifact is the local-fork reproduction of the pinned evidence bundle and direct-state/event-fold comparison, not an exploit.

The first reportable security conclusion requires all of:

```
scope
+ exact code/version
+ invariant violation
+ isolated reproduction
+ in-scope impact
+ permitted attacker preconditions
+ novelty
+ minimal PoC
```

## Source index

- USDT0 deployments: https://docs.usdt0.to/technical-documentation/deployments
- USDT0 technical docs: https://docs.usdt0.to/
- LayerZero EndpointV2: https://github.com/LayerZero-Labs/LayerZero-v2/blob/main/packages/layerzero-v2/evm/protocol/contracts/EndpointV2.sol
- LayerZero OAppCore: https://github.com/LayerZero-Labs/LayerZero-v2/blob/main/packages/layerzero-v2/evm/oapp/contracts/oapp/OAppCore.sol
- LayerZero OFTCore: https://github.com/LayerZero-Labs/LayerZero-v2/blob/main/packages/layerzero-v2/evm/oapp/contracts/oft/OFTCore.sol
- LayerZero MessageLibManager: https://github.com/LayerZero-Labs/LayerZero-v2/blob/main/packages/layerzero-v2/evm/protocol/contracts/MessageLibManager.sol
- LayerZero ReceiveUln302: https://github.com/LayerZero-Labs/LayerZero-v2/blob/main/packages/layerzero-v2/evm/messagelib/contracts/uln/uln302/ReceiveUln302.sol
- LayerZero SendUln302: https://github.com/LayerZero-Labs/LayerZero-v2/blob/main/packages/layerzero-v2/evm/messagelib/contracts/uln/uln302/SendUln302.sol
- Dedaub LayerZero V2 reference: https://github.com/Dedaub/monitoring-cli/blob/9638b65aba28471ee2b0f81cfcf3f3ed10b686a3/packages/dedaub-skills/dedaub_skills/skills/dedaub-monitoring/references/protocols/layerzero/v2.md
- USDT0 audit repository: https://github.com/Everdawn-Labs/usdt0-audit-reports

## Repository state

PR #22 is a draft against `feat/reentrancy-lab`.

As of capture:
- PR head: `bbc08fb07df04deeef5b25447da9259442ceaf95`
- workflow runs observed for that head: none returned by the GitHub connector

Therefore:
- benchmark: OPEN / UNVERIFIED
- resolver: OPEN / UNVERIFIED
- target vulnerability status: NONE_CLAIMED


## Exact-code finding

The current implementation is now **ESTABLISHED at the bytecode/source level**:

- Sourcify v2: `exact_match`
- compiler: Solidity `0.8.22+commit.4fc1097e`
- contract: `OAdapterUpgradeable`
- creation and runtime matches: `exact_match`
- USDT0-specific implementation is a thin wrapper over LayerZero `OFTAdapterUpgradeable`
- constructor explicitly calls `_disableInitializers()`

The repository commit that produced this implementation remains **UNKNOWN**.

Security consequence: the unexplored surface shifts from custom Ethereum adapter logic toward deployment/configuration state: peer, receive library, effective ULN/DVN configuration, history, and cross-chain state correspondence.

See `targets/usdt0/USDT0-IOTA-LOCKBOX-CODE-MODEL-v0.1.md`.


## Newly eliminated ambiguity: receive-library grace period

A current receive-library address alone is insufficient. LayerZero MessageLibManager can temporarily accept a previous receive library during a block-bounded grace period. Therefore the target snapshot must include:

app receive library + default receive library + effective/current library + timeout library + expiry block + pinned block.

This is now enforced structurally by reentrancy-lab/tools/validate_layerzero_snapshot.py.
