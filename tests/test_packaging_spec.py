"""Tests for PyInstaller packaging configuration."""

import ast
from pathlib import Path
import unittest


class TestPackagingSpec(unittest.TestCase):
    """Packaging should follow platform-specific PyInstaller patterns."""

    def setUp(self):
        source = Path("bongo_cat.spec").read_text(encoding="utf-8")
        self.tree = ast.parse(source)

    def _assigns_name_from_call(self, target_name, call_name):
        return [
            node for node in ast.walk(self.tree)
            if (
                isinstance(node, ast.Assign)
                and any(
                    isinstance(target, ast.Name) and target.id == target_name
                    for target in node.targets
                )
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == call_name
            )
        ]

    def test_macos_bundle_uses_collected_onedir_app(self):
        """macOS .app bundles should wrap COLLECT output, not the one-file exe."""
        collect_assignments = self._assigns_name_from_call("coll", "COLLECT")
        bundle_assignments = self._assigns_name_from_call("app", "BUNDLE")

        self.assertTrue(collect_assignments)
        self.assertTrue(bundle_assignments)

        bundle_call = bundle_assignments[0].value
        self.assertIsInstance(bundle_call.args[0], ast.Name)
        self.assertEqual("coll", bundle_call.args[0].id)

    def test_macos_bundle_sets_version_metadata(self):
        bundle_assignments = self._assigns_name_from_call("app", "BUNDLE")
        self.assertTrue(bundle_assignments)

        keywords = {keyword.arg: keyword.value for keyword in bundle_assignments[0].value.keywords}

        self.assertIn("version", keywords)
        self.assertIn("info_plist", keywords)

        info_plist = keywords["info_plist"]
        self.assertIsInstance(info_plist, ast.Dict)
        plist_keys = {
            key.value for key in info_plist.keys
            if isinstance(key, ast.Constant)
        }

        self.assertIn("CFBundleShortVersionString", plist_keys)
        self.assertIn("CFBundleVersion", plist_keys)


if __name__ == "__main__":
    unittest.main()
