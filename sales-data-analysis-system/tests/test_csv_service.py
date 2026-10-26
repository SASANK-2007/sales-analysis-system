import tempfile
import unittest
from pathlib import Path
from csv_service import validate_and_clean_csv

class CsvValidationTests(unittest.TestCase):
    def test_valid_and_invalid_rows(self):
        content = (
            "sale_date,product_name,category,quantity,unit_price,region\n"
            "2026-01-01,Pen,Stationery,2,10.00,South\n"
            "not-a-date,Book,Education,1,50.00,West\n"
            "2026-01-03,Notebook,Stationery,-2,20.00,South\n"
        )
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "test.csv"
            path.write_text(content, encoding="utf-8")
            df, errors = validate_and_clean_csv(path)
        self.assertEqual(len(df), 1)
        self.assertEqual(int(df.iloc[0]["quantity"]), 2)
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0]["row_number"], 3)
        self.assertEqual(errors[1]["row_number"], 4)

    def test_missing_column_raises_error(self):
        content = "sale_date,product_name\n2026-01-01,Pen\n"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "missing.csv"
            path.write_text(content, encoding="utf-8")
            with self.assertRaises(ValueError):
                validate_and_clean_csv(path)

if __name__ == "__main__":
    unittest.main()
