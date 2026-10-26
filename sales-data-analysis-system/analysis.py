from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def build_summary(df):
    if df.empty:
        return {"revenue": 0.0, "quantity": 0, "transactions": 0, "products": 0}
    revenue = np.sum(df["quantity"].to_numpy() * df["unit_price"].to_numpy())
    return {
        "revenue": float(revenue),
        "quantity": int(np.sum(df["quantity"].to_numpy())),
        "transactions": int(len(df)),
        "products": int(df["product_name"].nunique()),
    }

def build_product_ranking(df):
    if df.empty:
        return pd.DataFrame(columns=["product_name", "category", "quantity_sold", "revenue"])
    result = (df.groupby(["product_name", "category"], as_index=False)
        .agg(quantity_sold=("quantity", "sum"), revenue=("revenue", "sum"))
        .sort_values(["quantity_sold", "revenue"], ascending=False))
    result["revenue"] = result["revenue"].round(2)
    return result.head(10)

def build_monthly_trend(df):
    if df.empty:
        return pd.DataFrame(columns=["month", "revenue", "quantity_sold"])
    work = df.copy()
    work["month"] = work["sale_date"].dt.to_period("M").astype(str)
    result = (work.groupby("month", as_index=False)
        .agg(revenue=("revenue", "sum"), quantity_sold=("quantity", "sum"))
        .sort_values("month"))
    result["revenue"] = result["revenue"].round(2)
    return result

def create_charts(df, report_folder):
    folder = Path(report_folder)
    folder.mkdir(parents=True, exist_ok=True)

    # Monthly revenue line chart
    plt.figure(figsize=(9, 4.5))
    if not df.empty:
        monthly = df.assign(month=df["sale_date"].dt.to_period("M").astype(str)).groupby("month")["revenue"].sum()
        plt.plot(monthly.index, monthly.values, marker="o")
        plt.xticks(rotation=35, ha="right")
    else:
        plt.text(0.5, 0.5, "Upload a CSV to view monthly sales", ha="center", va="center")
        plt.xticks([])
        plt.yticks([])
    plt.title("Monthly Revenue Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.tight_layout()
    plt.savefig(folder / "monthly_trend.png", dpi=140)
    plt.close()

    # Top product bar chart
    plt.figure(figsize=(9, 4.5))
    if not df.empty:
        top = df.groupby("product_name")["quantity"].sum().sort_values(ascending=False).head(10)
        plt.bar(top.index.astype(str), top.values)
        plt.xticks(rotation=35, ha="right")
    else:
        plt.text(0.5, 0.5, "Upload a CSV to view product sales", ha="center", va="center")
        plt.xticks([])
        plt.yticks([])
    plt.title("Top Products by Quantity Sold")
    plt.xlabel("Product")
    plt.ylabel("Quantity sold")
    plt.tight_layout()
    plt.savefig(folder / "product_ranking.png", dpi=140)
    plt.close()
