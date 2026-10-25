# Sky PAU — missing evidence and next test gate (2026-10-25)

**Status:** Investigation gap review. No new vulnerability claimed. No exploit testing or external submission performed.  
**Purpose:** Prevent source/deployment conflation and avoid investing in known or not-yet-deployed behavior.

## Summary

The PAU × Spotter stale-price hypothesis was disproved for the pinned Grove allocator setup. That is a negative result for one mechanism, not a completed bounty audit.

The next major omission is **an exact deployment-to-source-to-audit map for the relevant live PAU controller**, plus a novelty and attacker-capability gate before running a local-fork PoC.

## 1. Separate the stacks before tracing more

The current official [Spark address registry](https://github.com/sparkdotfi/spark-address-registry/blob/master/src/Ethereum.sol) records these distinct Ethereum deployments:

| Deployment | Address | Registry-pinned version/source |
|---|---|---|
| Shared Spark PAU Beacon | `0xd47230358AB6c52A0a988150Ac4Ab888FE8B7786` | `diamond-pau` commit `cbf71b2`, v1.14.0 |
| SPUSDC PAU Controller | `0x4623cdEf0FB92499fd20f710318Cf17B8a7EB6bC` | `diamond-pau` commit `cbf71b2`, v1.14.0 |
| SPUSDC PAU ALMProxy | `0x8D719A830b00e5571db00D173505CD56c0Ec224a` | `diamond-pau` commit `cbf71b2`, v1.14.0 |
| SPUSDC PAU AccessControls | `0x36F61446638BE126a189689552f38159d30f95ef` | `diamond-pau` commit `cbf71b2`, v1.14.0 |
| SPUSDC PAU RateLimits | `0x222712581c3631DDF938f98Dab29a6D098ec6829` | `diamond-pau` commit `cbf71b2`, v1.14.0 |
| Spark Liquidity Layer legacy Controller | `0x5c46Fc65855c0C7465a1EA85EEA0B24B601502D3` | `spark-alm-controller` commit `984ec54`, v1.10.0 |
| Spark Liquidity Layer legacy ALMProxy | `0x1601843c5E9bC251A3272907010AFa41Fa18347E` | `spark-alm-controller` commit `6058f68`, v1.0.0 |

The Grove allocator vault `ALLOCATOR-GROVE-A` is another piece of the system and was verified separately. Do not assume that every address and code path from `diamond-pau/dev`, the SPUSDC PAU, the legacy SLL controller, and the Grove allocator is one interchangeable deployment.

### Still to verify directly at a pinned block

- The live SPUSDC Controller's `proxy()`, `beacon()`, `rateLimits()`, and local integration dispatch map.
- The actual `USDSFacet.vault()` value and whether it is the exact Grove vault under discussion.
- The set of addresses holding the `CONTROLLER` role on each ALMProxy; in particular, whether the SPUSDC PAU proxy is actually shared by multiple active Controllers.
- The role members and live rate-limit configuration for each candidate path.
- Runtime bytecode/source matches and the precise latest active deployment state, not only an address-registry source comment.

Until these points are resolved, the current code trace is not a complete trace of the production path.

## 2. Version and bounty eligibility gap

The address registry pins the SPUSDC PAU to `diamond-pau` v1.14.0 / commit `cbf71b2`. The repo's `dev` branch was updated later (observed commit `c5c961a8bd5568c7ca73ba1151b23ab9c7cd9113`). Current-development code must not be treated as deployed until its release/bytecode mapping is established.

The recent [SwapFacet PR #234](https://github.com/sky-ecosystem/diamond-pau/pull/234) was still **open and draft** as of this review. It describes a new PAU-to-PAU swap path; that code is not a live bounty target merely because it exists in a public branch. Preserve it as pre-deployment research only, unless deployment evidence changes.

The repository includes versioned audit reports for PAU, including the v1.14.0 Cantina and ChainSecurity reports under `audits/`. We have not yet reconciled those reports line-by-line against the deployed `cbf71b2` code and current Sky Immunefi known issues. This is a real gap: no claim about sparse audit coverage or issue novelty should be made until that reconciliation is complete.

## 3. Multi-Controller reentrancy: documented, not a finding

The repo's [architecture document](https://github.com/sky-ecosystem/diamond-pau/blob/dev/docs/ARCHITECTURE.md) explicitly states that when sibling Controllers share one ALMProxy, reentrancy guards live in each Controller's storage, so a guard in one Controller does not lock the other.

This discussion was added in merged [PR #203](https://github.com/sky-ecosystem/diamond-pau/pull/203) on June 3, 2026, following the multi-controller topology introduced in [PR #202](https://github.com/sky-ecosystem/diamond-pau/pull/202). Therefore:

- The pattern is publicly documented and is not novel by itself.
- Its relevance to the active deployment remains unverified: we must prove that two active Controllers actually share the same ALMProxy.
- Any bounty hypothesis would need a separate, not-already-disclosed invariant violation, a real untrusted callback path, a demonstrated in-scope loss, and known-issue/audit clearance.
- An attack that simply assumes a compromised trusted/privileged allocator or Controller should not be mistaken for a permissionless bounty finding.

## 4. What an eligible next test must prove

A useful local-fork test must be written against the exact eligible deployed bytecode/state (or a demonstrably equivalent pinned release), not only today's `dev` tree.

1. **Reachability:** Identify a public or otherwise in-scope unprivileged caller path into the operation; no assumption that the attacker already owns an excluded privileged role.
2. **Topology:** Show that the path touches at least two active Controllers sharing the same ALMProxy, if investigating cross-controller reentrancy.
3. **Invariant:** Specify a concrete check-then-act invariant such as balance delta, minimum output, position ownership, or pending-request state that becomes false under the exact call sequence.
4. **Counterexample:** Produce a deterministic local-fork reproduction showing a state/asset delta not permitted by the operation's rate limit, slippage floor, and custody policy.
5. **Controls:** Run the same test without the callback and with the sibling Controller path disabled; show that the bad state is eliminated.
6. **Eligibility:** Reconcile the result against the v1.14.0 audit reports, Sky scope and known issues, trusted-role exclusions, and payout rules.
7. **Stop gate:** If there is only one active Controller for the relevant proxy, no reachable callback, no violated invariant, or the behavior is already disclosed/known, kill the hypothesis and move to a different deployed public-call path.

No production transaction should be used for these checks. Stay within the bounty's permitted local-fork environment.

## Evidence labels

| Claim | Label | Basis |
|---|---|---|
| Grove allocator `PIP_ALLOCATOR` is a fixed 1:1 oracle at Ethereum block 26,267,615 | `ESTABLISHED` | Direct read-only state/source check recorded in [the PAU × Spotter recheck](PAU-SPOTTER-STALE-PRICE-RECHECK_2026-10-25.md). |
| The address registry distinguishes SPUSDC PAU from the legacy SLL Controller/Proxy and pins version comments | `ESTABLISHED` | Current registry source, linked above. |
| Multi-controller reentrancy guards are scoped per Controller, not per ALMProxy | `ESTABLISHED / DISCLOSED` | Current architecture docs and merged PR #203. |
| Multiple active Controllers currently share the SPUSDC PAU ALMProxy | `UNKNOWN` | Role membership and full live proxy/controller topology not yet queried. |
| The new SwapFacet PR is deployed and eligible | `CONTRADICTED` by current repository state | PR #234 remained open and draft at review time; no deployment evidence. |
| PAU v1.14.0 audit reports/known issues have been fully reconciled against the actual deployed call path | `OPEN` | Work remains; no completeness claim made. |

## Decision

**Do not resume the stale-price hypothesis. Do not submit the documented multi-controller pattern as-is.** Next work is deployment-state pinning and v1.14.0 audit reconciliation, then one local-fork experiment only if the deployment actually contains the topology and a distinct public caller path survives the eligibility gate.
