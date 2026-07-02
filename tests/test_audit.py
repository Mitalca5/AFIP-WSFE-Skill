import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_secrets


class AuditSecretsTest(unittest.TestCase):
    def test_allows_fictional_cuits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "example.txt").write_text("20111111112 20222222223 20333333334", encoding="utf-8")
            self.assertEqual(audit_secrets.audit(root), [])

    def test_flags_unexpected_cuit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "bad.txt").write_text("20" + "999999999", encoding="utf-8")
            findings = audit_secrets.audit(root)
            self.assertTrue(any("unexpected CUIT-like" in finding for finding in findings))


if __name__ == "__main__":
    unittest.main()
