"""Opt-in proof that the production Excel COM adapter works end to end.

This creates an unprotected disposable workbook; it proves the ordinary COM
boundary and source immutability, not the separately gated DRM workflow.
"""

from __future__ import annotations

import gc
import hashlib
import os
from pathlib import Path
import tempfile
import unittest

from app.excel.com_adapter import ComExtractionAdapter
from app.excel.session import _com_modules


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@unittest.skipUnless(
    os.name == "nt" and os.environ.get("RUN_EXCEL_COM_SMOKE") == "1",
    "set RUN_EXCEL_COM_SMOKE=1 on an authorized Windows/Excel machine",
)
class TestExcelComSmoke(unittest.TestCase):
    def _create_workbook(self, path: Path) -> None:
        pythoncom, client, _ = _com_modules()
        pythoncom.CoInitialize()
        application = None
        workbook = None
        worksheet = None
        try:
            application = client.DispatchEx("Excel.Application")
            application.Visible = False
            application.DisplayAlerts = False
            workbook = application.Workbooks.Add()
            worksheet = workbook.Worksheets(1)
            worksheet.Name = "Data"
            worksheet.Range("A1:C4").Value2 = (
                ("order_id", "quantity", "region"),
                ("A-100", 10, "North"),
                ("A-101", 20, "South"),
                ("A-102", 30, "West"),
            )
            workbook.SaveAs(str(path), FileFormat=51)
        finally:
            if workbook is not None:
                workbook.Close(SaveChanges=False)
            if application is not None:
                application.Quit()
            worksheet = None
            workbook = None
            application = None
            pythoncom.CoUninitialize()
            gc.collect()

    def test_two_production_reads_preserve_source_bytes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="excel-com-smoke-") as temp:
            source = Path(temp) / "source.xlsx"
            self._create_workbook(source)
            original_hash = _sha256(source)
            config = {
                "report_id": "com-smoke",
                "run_id": "RUN-COM-SMOKE",
                "schema_version": "1",
                "excel": {
                    "open_mode": "dedicated",
                    "sheet": "Data",
                    "data_area": "range:A1:C4",
                },
                "extraction": {
                    "projected_columns": ["region", "order_id", "quantity"],
                    "min_rows_per_chunk": 1,
                    "max_rows_per_chunk": 2,
                    "target_cells_per_chunk": 6,
                },
            }

            for _ in range(2):
                adapter = ComExtractionAdapter()
                try:
                    identity = adapter.open(str(source), config)
                    chunks = list(adapter.chunks())
                    self.assertEqual(identity.open_mode, "dedicated")
                    self.assertEqual(
                        [row for chunk in chunks for row in chunk.values],
                        [
                            ("North", "A-100", 10.0),
                            ("South", "A-101", 20.0),
                            ("West", "A-102", 30.0),
                        ],
                    )
                    self.assertTrue(adapter.source_unchanged())
                finally:
                    adapter.close()

            self.assertEqual(_sha256(source), original_hash)


if __name__ == "__main__":
    unittest.main()
