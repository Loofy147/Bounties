# Verified Source Pin Comparator

Offline utility for comparing one Solidity source unit returned by Sourcify API v2 with a source file pinned to a repository commit. It does not fetch URLs, run an EVM, or decide bounty eligibility.

## Example

    python tools/source_pin/compare_verified_source.py \
      --verified-json artifacts/transitstation-sourcify-v2.json \
      --source-unit src/transit/TransitStation.sol \
      --repo-file vendor/pxl-boring-vault/src/transit/TransitStation.sol \
      --output evidence/transitstation-source-compare.json

Save the API response from GET /v2/contract/{chainId}/{address}?fields=sources,metadata as a local JSON file first. Record the address, chain, pinned repository commit, file blob SHA and acquisition timestamp with the output.

## Results and gate

- EXACT_TEXT_MATCH (exit 0): source unit texts are byte-for-byte equal.
- COMMENT_OR_WHITESPACE_ONLY_DIFF (exit 1): comments/spacing differ but the conservative normalized token text matches. This is diagnostic only; strict source pin remains open.
- SOURCE_CONTENT_MISMATCH (exit 3): normalized content differs.
- INPUT_ERROR / OUTPUT_ERROR (exit 2): malformed/missing inputs.

The tool is fail-closed: comment-only matches do not pass the exact-pin gate. A reviewer must still establish deployed address/chain/block, runtime bytecode hash, compiler settings, constructor arguments and immutable values, complete dependency source map, and current program eligibility. A comment-only mismatch can affect compiler metadata and must not be described as bytecode identity.

## Tests

    python -m unittest discover -s tools/source_pin -v

The repository workflow `.github/workflows/source-pin-comparator.yml` runs this suite on pushes and pull requests that touch the comparator, tests, or workflow. Treat the GitHub Actions result as the shared verification record; a local unit-test pass alone does not prove source-to-deployment equivalence.
