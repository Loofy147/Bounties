import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from compare_verified_source import (
    compare_sources,
    load_verified_source,
    main,
    solidity_lexical_form,
)


class SolidityLexicalFormTests(unittest.TestCase):
    def test_comments_and_formatting_are_ignored_for_diagnostic_only(self):
        left = "pragma solidity 0.8.21; // deployed note\ncontract A { uint256 x; }"
        right = "pragma solidity 0.8.21;\n/* repository note */ contract A {\n uint256 x;\n}"
        result = compare_sources(left, right)
        self.assertFalse(result["exact_text_match"])
        self.assertTrue(result["comment_whitespace_normalized_match"])
        self.assertEqual(result["status"], "COMMENT_OR_WHITESPACE_ONLY_DIFF")

    def test_actual_code_difference_is_not_normalized_away(self):
        left = "contract A { uint256 public x; }"
        right = "contract A { uint256 public y; }"
        result = compare_sources(left, right)
        self.assertFalse(result["exact_text_match"])
        self.assertFalse(result["comment_whitespace_normalized_match"])
        self.assertEqual(result["status"], "SOURCE_CONTENT_MISMATCH")

    def test_comment_markers_inside_string_are_preserved(self):
        left = 'string constant URL = "https://example.test/a/*not-comment*/";'
        right = 'string constant URL = "https://example.test/a/";'
        self.assertNotEqual(solidity_lexical_form(left), solidity_lexical_form(right))
        self.assertEqual(compare_sources(left, right)["status"], "SOURCE_CONTENT_MISMATCH")

    def test_unterminated_block_comment_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "unterminated Solidity block comment"):
            solidity_lexical_form("contract A { /* unterminated")


class VerifiedSourceLoadingTests(unittest.TestCase):
    def test_loads_sourcify_v2_source_unit_and_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata_path = root / "verified.json"
            source_path = root / "A.sol"
            metadata_path.write_text(json.dumps({
                "address": "0xabc",
                "chainId": 1,
                "match": "exact_match",
                "verifiedAt": "2026-10-21T00:00:00Z",
                "metadata": {
                    "compiler": {"version": "0.8.21+commit.d9974bed"},
                    "settings": {"optimizer": {"enabled": True, "runs": 200}, "evmVersion": "shanghai"},
                },
                "sources": {"src/A.sol": {"content": "contract A {}"}},
            }), encoding="utf-8")
            source_path.write_text("contract A {}", encoding="utf-8")
            loaded, metadata = load_verified_source(metadata_path, "src/A.sol")
            self.assertEqual(loaded, "contract A {}")
            self.assertEqual(metadata["verification_match"], "exact_match")
            self.assertEqual(metadata["optimizer"]["runs"], 200)

    def test_missing_source_unit_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "verified.json"
            path.write_text(json.dumps({"sources": {}}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "has no embedded 'content'"):
                load_verified_source(path, "src/Missing.sol")


class CliFailClosedTests(unittest.TestCase):
    def _run_cli(self, verified_source: str, repo_source: str) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata_path = root / "verified.json"
            repo_path = root / "A.sol"
            metadata_path.write_text(json.dumps({
                "chainId": 1,
                "address": "0xabc",
                "match": "exact_match",
                "metadata": {"compiler": {"version": "0.8.21"}},
                "sources": {"src/A.sol": {"content": verified_source}},
            }), encoding="utf-8")
            repo_path.write_text(repo_source, encoding="utf-8")
            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main([
                    "--verified-json", str(metadata_path),
                    "--source-unit", "src/A.sol",
                    "--repo-file", str(repo_path),
                ])
            return code, stdout.getvalue()

    def test_cli_exact_text_match_exits_zero(self):
        code, output = self._run_cli("contract A {}", "contract A {}")
        self.assertEqual(code, 0)
        self.assertIn('"status": "EXACT_TEXT_MATCH"', output)

    def test_cli_comment_only_difference_fails_closed(self):
        code, output = self._run_cli("contract A {} // verified note", "contract A {} // repo note")
        self.assertEqual(code, 1)
        self.assertIn('"status": "COMMENT_OR_WHITESPACE_ONLY_DIFF"', output)

    def test_cli_semantic_difference_exits_three(self):
        code, output = self._run_cli("contract A { uint x; }", "contract A { uint y; }")
        self.assertEqual(code, 3)
        self.assertIn('"status": "SOURCE_CONTENT_MISMATCH"', output)


if __name__ == "__main__":
    unittest.main()
