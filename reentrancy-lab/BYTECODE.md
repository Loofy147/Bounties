# The one gap left genuinely open: bytecode-only analysis

Everything in this lab starts from source. That's not how $36.7M of 2026 losses happened — those came from contracts whose source was deliberately left unverified, on the assumption that obscurity was a defense. AI-assisted decompilation is closing that gap for attackers faster than most researchers have adapted, which makes bytecode-level reading an increasingly non-optional skill, not an optional one.

This wasn't built out in this session — the sandbox's tooling budget went to the nine executable modules instead — so here's exactly where to pick it up, concretely:

- **Mythril, bytecode mode**: `myth analyze -c <hex bytecode>` runs the same symbolic execution engine against raw bytecode with no source needed at all.
- **Heimdall-rs**: purpose-built EVM bytecode decompiler; turns raw bytecode into pseudo-Solidity, recovers function signatures from selectors even with no ABI.
- **Panoramix / Dedaub decompiler**: web-based decompilation, good for a fast first read of an unverified contract before committing to deeper tooling.
- **4byte.directory**: reverse-looks-up function selectors against a public database of known signatures — the first move on any unverified contract, since most "custom" functions turn out to be standard ones once you match the selector.

Concrete exercise, if you want to close this yourself: take any compiled bytecode from this repo (`compile.js` outputs `evm.bytecode.object` for every module), strip the source, and run it through Mythril's bytecode mode cold. Compare what it finds against what Slither found on the real source in each module's run above — that comparison is the actual skill.
