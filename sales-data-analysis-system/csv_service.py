import pandas as pd

REQUIRED_COLUMNS = [
    "sale_date", "product_name", "category", "quantity", "unit_price", "region"
]

def validate_and_clean_csv(path):
    """
    Required CSV columns:
    sale_date, product_name, category, quantity, unit_price, region

    Returns (clean_dataframe, errors). Data rows are numbered starting at 2
    because row 1 is the CSV header.
    """
    try:
        raw = pd.read_csv(path, dtype=str, keep_default_na=False)
    except Exception as exc:
        raise ValueError(f"CSV could not be read: {exc}")

    raw.columns = [str(c).strip().lower() for c in raw.columns]
    missing = [col for col in REQUIRED_COLUMNS if col not in raw.columns]
    if missing:
        raise ValueError("Missing required column(s): " + ", ".join(missing))

    cleaned = []
    errors = []
    for index, row in raw.iterrows():
        csv_row_number = index + 2
        try:
            values = {col: str(row[col]).strip() for col in REQUIRED_COLUMNS}
            for col in ("product_name", "category", "region"):
                if not values[col]:
                    raise ValueError(f"{col} cannot be empty")

            date = pd.to_datetime(values["sale_date"], errors="raise")
            if pd.isna(date):
                raise ValueError("sale_date is invalid")

            quantity = int(values["quantity"])
            if quantity <= 0:
                raise ValueError("quantity must be a positive integer")

            price = float(values["unit_price"])
            if price < 0:
                raise ValueError("unit_price cannot be negative")
            if price != price or price == float("inf") or price == float("-inf"):
                raise ValueError("unit_price must be a finite number")

            cleaned.append({
                "sale_date": date.normalize(),
                "product_name": values["product_name"],
                "category": values["category"],
                "quantity": quantity,
                "unit_price": round(price, 2),
                "region": values["region"],
            })
        except Exception as exc:
            errors.append({"row_number": csv_row_number, "error": str(exc)})

    return pd.DataFrame(cleaned, columns=REQUIRED_COLUMNS), errors
