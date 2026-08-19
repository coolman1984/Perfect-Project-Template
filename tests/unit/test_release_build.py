from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from app.release_main import verify_package
from tools.build_release import tree_hash


class TestReleaseIntegrity(unittest.TestCase):
    def test_manifest_detects_missing_and_changed_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            payload = root / "app" / "application.bin"
            payload.parent.mkdir()
            payload.write_bytes(b"sealed")
            digest = hashlib.sha256(payload.read_bytes()).hexdigest()
            (root / "checksums.sha256").write_text(
                f"{digest} *app/application.bin\n", encoding="utf-8")
            self.assertEqual(verify_package(root), [])

            payload.write_bytes(b"tampered")
            self.assertEqual(
                verify_package(root),
                ["checksum mismatch app/application.bin"])

    def test_tree_hash_is_order_independent_and_content_sensitive(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "first.txt"
            second = root / "second.txt"
            first.write_text("one", encoding="utf-8")
            second.write_text("two", encoding="utf-8")
            expected = tree_hash([first, second], root)
            self.assertEqual(expected, tree_hash([second, first], root))
            second.write_text("changed", encoding="utf-8")
            self.assertNotEqual(expected, tree_hash([first, second], root))


if __name__ == "__main__":
    unittest.main()
