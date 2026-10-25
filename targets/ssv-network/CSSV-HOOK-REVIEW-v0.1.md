# SSV v2.0.0 — cSSV transfer-hook review v0.1

**Status:** no hook vulnerability reproduced; the allowance-order lead is CONTRADICTED.  
**Scope pin:** ssvlabs/ssv-network@v2.0.0, commit 9bb7b21d4432f34f623bed3e0bb3fa77f1e5d2b9.

## Call-order trace

### transferFrom

1. OpenZeppelin ERC20 transferFrom checks/spends allowance, then calls _transfer.
2. ERC20 _transfer calls _beforeTokenTransfer(from, to, amount) before changing either balance.
3. CSSVToken._beforeTokenTransfer calls SSVStaking.onCSSVTransfer for a non-self, non-mint/burn, positive-amount transfer not initiated by staking.
4. onCSSVTransfer checks msg.sender == CSSV_ADDRESS, calls _syncFees, then _settle(from) and _settle(to).
5. _settle reads CSSVToken.balanceOf(user), so it observes pre-transfer balances. Allowance decrement does not change balanceOf and cannot make settlement use a post-transfer share count.
6. Only after the hook returns does ERC20 update sender and recipient balances.

Primary sources: [CSSVToken hook](https://github.com/ssvlabs/ssv-network/blob/v2.0.0/contracts/token/CSSVToken.sol#L26-L39), [SSVStaking settlement](https://github.com/ssvlabs/ssv-network/blob/v2.0.0/contracts/modules/SSVStaking.sol#L173-L228), [OpenZeppelin ERC20 API](https://docs.openzeppelin.com/contracts/4.x/api/token/erc20). The v2.0.0 lockfile declares OpenZeppelin Contracts ^4.9.6.

Therefore “allowance is spent before the hook, so owner rewards settle after balance debit” does not follow: allowance and balance are separate state variables, and the balance debit occurs after the hook.

## Unstake and mint/burn boundaries

requestUnstake calls _syncFees, reads the holder's current cSSV balance, settles with that balance, validates the amount, and only then calls CSSVToken.burn. Mint/burn use zero-address endpoints excluded by CSSVToken._beforeTokenTransfer; staking settles explicitly before mint/burn. An immediate unstake after receiving cSSV therefore does not rely on the hook running during burn and does not double-credit the received shares.

Source: [SSVStaking.requestUnstake](https://github.com/ssvlabs/ssv-network/blob/v2.0.0/contracts/modules/SSVStaking.sol#L65-L92).

## Candidate triage

| Candidate seam | Source/test evidence | Disposition |
|---|---|---|
| transferFrom allowance order | Source proves hook runs before balance mutation. No focused transferFrom test was found in the inspected transfer E2E file. | KILLED BY SOURCE TRACE; a regression test could improve coverage, but this is not a vulnerability claim. |
| Transfer then immediate requestUnstake | requestUnstake settles before burn; existing unit tests cover a receiver unstaking after transfer and settlement before unstaking. | NO VIOLATION IDENTIFIED. A bundled same-transaction test would add coverage, not prove a bug. |
| Multi-hop A→B→C in one unchanged accumulator window | Existing tests cover chains across changing accumulator stages but do not explicitly label a fixed-accumulator window. | NOT REPRODUCED; reference model preserves accrued amounts at each boundary. |
| Dust with one cSSV wei | Unit tests cover a receiver holding exactly one wei. Claim rounds down to a multiple of 100,000 wei; with nonzero cSSV balance, accrued dust can combine with later fees. | NOT A THEFT FINDING; payout delay/rounding only on current evidence. |
| Permissionless syncFees before transfer | Transfer hook also calls _syncFees; fee distribution follows balances at synchronization time. | NO DISTINCT LOSS MECHANISM ESTABLISHED. |
| Self-transfer, zero transfer, mint, burn bypass the hook | Token deliberately skips hook for transitions that do not move shares between distinct holders. | EXPECTED BY CODE; relevant self/zero/mint/burn cases exist in E2E tests. |

## Reference-model outcomes

Five cSSV model tests cover transferFrom settlement on pre-transfer balance; transfer then immediate unstake without double-credit; same-accumulator multi-hop transfer without reward erasure/duplication; unstake after a later fee window using the holder's then-current balance; and one-wei remainder accumulating to a payable payout threshold.

All five pass. This model is not Solidity execution and is not evidence of production security.

## Focused upstream regression tests, if coverage is expanded

1. transferFrom with finite allowance: assert two settlement events, sender accrual based on pre-transfer balance, correct post-transfer balances and allowance.
2. A→B→C in one fixed accumulator epoch: assert no duplicate/erased rewards and exact expected accrued values.
3. Transfer receiver → requestUnstake with no intervening new fees: assert the pre-transfer epoch is not reassigned to the receiver and settlement precedes burn.

These are coverage improvements. A bounty candidate requires a failing target-contract test plus a concrete value-transfer or invariant violation on the exact eligible implementation.
