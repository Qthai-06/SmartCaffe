import os
import tempfile
import unittest
from unittest.mock import patch

from src.database import get_audit_log, get_latest_inventory, save_inventory


class DatabaseTests(unittest.TestCase):
    def test_save_inventory_and_audit_log(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "smartcafe.db")
            csv_path = os.path.join(tmpdir, "inventory.csv")

            with patch.dict(os.environ, {"SMARTCAFE_DB_PATH": db_path}, clear=False):
                with patch("src.database._csv_path", return_value=csv_path):
                    save_inventory(
                        {"cafe_hat": 10, "cafe_xay": 5, "ly_giay": 100, "ly_nhua": 50, "sua_dac": 12},
                        source="test",
                        actor="tester",
                    )
                    save_inventory(
                        {"cafe_hat": 8, "cafe_xay": 5, "ly_giay": 90, "ly_nhua": 45, "sua_dac": 11},
                        source="test",
                        actor="tester",
                        previous_counts={"cafe_hat": 10, "cafe_xay": 5, "ly_giay": 100, "ly_nhua": 50, "sua_dac": 12},
                        reason="manual_fix",
                    )

                    latest = get_latest_inventory()
                    self.assertEqual(latest["cafe_hat"], 8)
                    self.assertEqual(latest["ly_giay"], 90)

                    audit_df = get_audit_log(limit=50)
                    self.assertFalse(audit_df.empty)
                    self.assertIn("Mặt hàng", audit_df.columns)


if __name__ == "__main__":
    unittest.main()
