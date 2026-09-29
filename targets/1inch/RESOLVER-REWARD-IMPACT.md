
# NativeOrder Resolver Reward — Economic Impact Characterization

Snapshot: 2026-09-29
Target: 1inch Limit Order Protocol 4.3.4
Commit: 7da29889efa2e635611e1caf60f85f595ff7f05f

## Exact accounting model

Let:

- (C) = maker-owned WETH balance remaining in the clone immediately before resolver cancellation;
- (T) = resolver-funded WETH top-up transferred to the clone before cancellation;
- (B=C+T), assuming no other balance component;
- (R=min(rewardLimit, block.basefee times 70,000 times 1.1)).

The 4.3.4 resolver-cancellation path reads the clone's full WETH balance, unwraps it, pays (R) to the resolver, then sends (B-R) to the maker.

For the undercollateralized condition (C<R), choosing (T=R-C) makes (B=R). The cancellation then succeeds with maker proceeds equal to zero.

Therefore the maker-side value removed by the reward path is:

    maker loss = C

The reproduced mechanism can therefore consume 100% of the maker's residual clone collateral when the resolver supplies the missing balance needed to satisfy the reward subtraction.

## 10 gwei calibration

At a 10 gwei base fee:

    R = 70,000 x 10 gwei x 1.1 = 0.00077 ETH

The current calibration control uses:

- C = 0.0007 ETH
- T = 0.00007 ETH
- R = 0.00077 ETH

Latest successful calibration execution:
- GitHub Actions run #51
- job 109265719467
- research head e39993268632cc0b758ec7be98cd31048699949c

Observed output:

- maker residual/cancellation loss: 0.0007 ETH
- resolver reward: 0.00077 ETH
- cancellation gas used: 56,627
- effective gas price: 11 gwei
- cancellation transaction gas cost: 0.000622897 ETH

The calibration measures victim loss and reward transfer separately. It does not claim resolver profitability.

## Full resolver economics

A complete attack-cost model must include:

1. reward top-up;
2. gas to acquire/wrap that top-up;
3. gas to transfer the top-up into the clone;
4. gas for the cancellation itself.

The earlier shorthand condition C > cancellation-only gas was incomplete as a full profitability test.

The dedicated partial-fill economic control measures complete resolver accounting from a balance snapshot taken before the top-up:

    reward = top-up + deposit gas + transfer gas + cancellation gas + net gain

Run #64 measured C=0.0007 ETH, T=0.00007 ETH, R=0.00077 ETH, deposit gas=0.000058871677453431 ETH, transfer gas=0.000032863279096389 ETH, cancellation gas=0.000675697 ETH, victim loss=0.0007 ETH, and resolver net=-0.00006743195654982 ETH.

Final execution is complete in run #64 (36621806098), job 109588790780, head 8b59d02804de118ac9bd5ee2f18e58a2d5cf8a38.

## Natural victim-state reachability

The upstream 4.3.4 test suite contains an ETH-maker-order partial-fill path:

- create a native order with 0.3 ETH-equivalent WETH collateral;
- fill 0.2;
- the clone retains 0.1 WETH;
- maker cancellation then refunds the remaining 0.1 WETH.

This establishes that residual clone collateral after partial fill is a normal protocol state, not a test-only balance injection.

Our dedicated control reproduced the same state transition with residual C below the reward cap and successfully executed resolver cancellation after expiry plus delay.

## Interpretation

Established:

- the resolver reward is funded from the clone's aggregate WETH balance;
- a resolver can locally supply the missing balance and consume the maker's entire residual C when C<R;
- residual C<R can arise after an ordinary partial fill;
- the 10 gwei calibration measured C=0.0007 ETH victim-side loss and R=0.00077 ETH reward transfer.

Still open:

- whether the behavior is already disclosed by an applicable audit/known issue;
- exact production deployment/version correspondence;
- exact production-scale victim-state prevalence;
- final submission eligibility under the current program.

This remains an impact characterization, not a severity or bounty determination.
