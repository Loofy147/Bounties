# Sky LayerZero USDS Rate-Limit Recheck

Date: 2026-10-25  
Target: SkyOFTAdapter (Ethereum mainnet) / USDS → Solana LayerZero pathway  
Disposition: **HYPOTHESIS CONTRADICTED — false positive caused by decoding amount words incorrectly. Do not submit.**

## Claim ledger

- **ESTABLISHED** — the deployed, verified `SkyOFTAdapter` at `0x1e1D42781FC170EF9da004Fb735f56F0276d01B8` wraps USDS at `0xdc035d45d973e3ec169d2276ddab16f1e407384f` and uses LayerZero Endpoint V2.
- **ESTABLISHED** — the adapter's configured Solana peer corresponds to `BEvTHkTyXooyaJzP8egDUC7WQK8cyRrq5WvERZNWhuah` (EID 30168).
- **ESTABLISHED** — `RateLimitsChanged` logs show that on 2026-05-11, both directions for EID 30168 were configured with a 86,400-second window and a limit of 5,000,000 USDS. No later `RateLimitsChanged` event was returned in the inspected range.
- **CONTRADICTED** — the initial claim that a successful 12.8-million-USDS transfer bypassed the 5-million limit. Correct decoding shows the 2026-10-24 transfer was 50,001 USDS, not 12.8 million.
- **ESTABLISHED** — among the 110 `OFTSent` events for EID 30168 returned between 2026-05-11 and 2026-10-24, the largest individual send was 816,400 USDS. The maximum observed rolling 24-hour aggregate was approximately 1,880,066.422544 USDS, below the 5-million limit.
- **CONTRADICTED** — the apparent inconsistency between `outboundRateLimits(30168)` and `getAmountCanBeSent(30168)`. The values are consistent once the ABI words and linear-decay formula are parsed correctly.
- **NOT ESTABLISHED** — no rate-limit bypass, unauthorized withdrawal, bridge insolvency, or other bounty-impact path.

## Pinned, reproducible evidence

### Limit configuration

The only `RateLimitsChanged((uint32,uint48,uint256)[],uint8)` events returned for this adapter from block 25,000,000 through the current head were four events in transaction:

- [Configuration transaction](https://etherscan.io/tx/0xb03f728b109246f53d8fbc88c6a35584b8df9e2f0281dfca6e6d401adb7230d6)
- Event block: 25,072,324
- Timestamp: 2026-05-11 14:01:23 UTC
- EID 30168: window 86,400 seconds; limit 5,000,000 USDS, for both inbound and outbound.

No `RateLimitsReset` events were returned in the inspected range.

### Latest transfer and state

Transaction [`0xa48043a3ed0748a35dcda1167e21e07fc921cb766d46312036cd1adcd7212193`](https://etherscan.io/tx/0xa48043a3ed0748a35dcda1167e21e07fc921cb766d46312036cd1adcd7212193) succeeded on 2026-10-24 at 23:16:35 UTC. Its `OFTSent` event for EID 30168 reports:

- `amountSentLD = amountReceivedLD = 50001000000000000000000` = **50,001 USDS**.
- At the latest observed block, `outboundRateLimits(30168)` decoded to:
  - `lastUpdated = 2026-10-24 23:16:35 UTC`
  - `window = 86,400 seconds`
  - `amountInFlight = 50,001 USDS`
  - `limit = 5,000,000 USDS`

Before that send, the getter returned `amountInFlight = 114,168.666666666666666667 USDS` with `lastUpdated = 2026-10-24 10:31:47 UTC`. By 23:16 UTC, the elapsed time was about 45,888 seconds. The code's linear decay is:

`decay = limit × elapsed / window ≈ 2,655,555.56 USDS`.

Since this decay exceeds the previous 114,168.67 USDS in-flight amount, the effective in-flight amount is zero and full capacity is available for the 50,001 USDS transfer. At the subsequent latest read, decay likewise exceeds the new 50,001 USDS amount, so `getAmountCanBeSent` correctly returned zero in-flight and 5,000,000 USDS available.

### Transfer-event audit

The 110 `OFTSent` logs returned for EID 30168 from block 25,000,000 through latest covered 2026-05-11 14:09:35 UTC through 2026-10-24 23:16:35 UTC:

- Maximum single send: **816,400 USDS** (2026-05-20).
- Maximum observed rolling 24-hour sum: **about 1,880,066.422544 USDS** (2026-06-03 through 2026-06-04).
- No send exceeded 5,000,000 USDS in the inspected logs.

These results are inconsistent with the initial “12.8M send” interpretation and consistent with the configured 5M rolling limit.

## Source and method

- Deployed source and ABI: [Etherscan contract page](https://etherscan.io/address/0x1e1D42781FC170EF9da004Fb735f56F0276d01B8#code)
- [SkyOFTAdapter.sol](https://github.com/sky-ecosystem/sky-oapp-oft/blob/main/contracts/SkyOFTAdapter.sol)
- [SkyRateLimiter.sol](https://github.com/sky-ecosystem/sky-oapp-oft/blob/main/contracts/SkyRateLimiter.sol)
- [Mainnet LayerZero configuration](https://github.com/sky-ecosystem/sky-oapp-oft/blob/main/oft.layerzero.mainnet.config.ts)

The EVM adapter checks rate capacity in `_debit()` before transferring USDS. `SkyRateLimiter._calculateDecay()` linearly decays in-flight volume over the configured window; it can return the full limit when accumulated volume has decayed to zero.

## Decision

**Close this candidate. Do not submit.** The apparent violation came from an erroneous interpretation of the ABI-encoded amount. No exploit was reproduced, and the corrected on-chain amounts and decay calculation agree with the specified limit logic. Redirect investigation effort to a distinct invariant or a different in-scope target rather than mutating this false lead.
