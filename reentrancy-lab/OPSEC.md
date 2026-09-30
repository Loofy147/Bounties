# The gap this lab can't close with Solidity

Everything in `contracts/` trains code-level auditing. That's real, valuable, and Immunefi-relevant skill. It is not the whole 2026 threat picture. Through August 2026, compromised private keys and infrastructure overtook smart contract bugs as DeFi's #1 loss vector for the first time on record — $1.3B across eight months. No amount of Slither runs or Foundry fuzzing touches this category. It needs a different checklist, so here it is, built from the actual 2026 incidents rather than generic advice.

## What actually happened
- **Step Finance, 2026 — $27.3M.** Treasury private key compromise. Not a contract bug; a key that shouldn't have been reachable, was.
- **Resolv Labs, 2026 — $23M.** Attacker breached AWS KMS and used the compromised signing key directly. The contracts were fine. The cloud IAM boundary wasn't.
- **IoTeX ioTube, 2026 — $4.4M.** Validator key compromise on a bridge.
- **Bybit, Feb 2025 — $1.46B** (context, not 2026, but the scale precedent): a compromised signer's device was used to alter what a Safe multisig's hardware wallet actually displayed and signed. The multisig threshold didn't help because the *inputs to signing* were the attack surface, not the threshold logic.

The common thread: every one of these passed a smart-contract audit fine, because there was nothing wrong with the contract.

## A checklist that would have mattered here

**Key custody**
- Is any single key capable of moving treasury funds without a second party? (Step Finance's failure mode.)
- Where do signing keys/material actually live — HSM, KMS, or a hot wallet? If KMS: who has IAM permissions to that key policy, and is that access logged and alerted on, not just restricted? (Resolv Labs' failure mode.)
- Are hardware wallets used for anything that displays a hash instead of full decoded calldata? A device showing "sign this hash" instead of "you are approving a transfer of $X to Y" is a blind-signing risk regardless of the wallet's own security.

**Multisig design**
- Threshold and signer count are necessary, not sufficient. Ask instead: are the signers' *environments* independent? Same cloud provider, same laptop image, same admin managing all of them defeats the purpose of "3-of-5."
- Is there a transaction simulation/verification step before signing (e.g., Wallet Guard-style calldata decoding) so a signer can't be shown one thing and sign another?

**Validator/relayer infrastructure (the bridge-specific version of this)**
- For any bridge or cross-chain messaging component: how many independent verifiers actually have to agree, and are they run by genuinely different operators? KelpDAO's $292M loss traced to a single-verifier LayerZero configuration — 1,200+ other OApp contracts were running the same minimal setup at the time. This is a config choice made at protocol-deployment time, invisible to a Solidity audit of the bridge contract itself.

**Incident response**
- Is there a tested (not just documented) pause/pause-guardian mechanism, and who can trigger it at 3am?
- Are treasury movements monitored in real time (Forta, custom alerting) so a compromised-key drain gets caught in minutes, not discovered post-mortem?

## What this is and isn't
This isn't a substitute for a real security engineering review of infrastructure and key management — that's a distinct discipline (cloud IAM, HSM/KMS design, org-level opsec) from smart contract auditing, and claiming otherwise would be dishonest. What it is: a way to know where the edge of the skillset this lab builds actually sits, so you're not surprised when a perfectly-audited contract still gets drained through the layer nobody audited.
