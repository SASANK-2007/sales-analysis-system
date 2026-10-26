import os
from pathlib import Path
from datetime import datetime

import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename

from config import Config
from database import get_connection, init_db, insert_sales, fetch_sales
from analysis import build_summary, build_product_ranking, build_monthly_trend, create_charts
from csv_service import validate_and_clean_csv, REQUIRED_COLUMNS

app = Flask(__name__)
app.config.from_object(Config)
app.config["UPLOAD_FOLDER"] = str(Path("uploads"))
app.config["REPORT_FOLDER"] = str(Path("reports"))
Path(app.config["UPLOAD_FOLDER"]).mkdir(exist_ok=True)
Path(app.config["REPORT_FOLDER"]).mkdir(exist_ok=True)

@app.before_request
def ensure_database():
    if not app.config.get("DB_INITIALIZED"):
        init_db()
        app.config["DB_INITIALIZED"] = True

@app.route("/")
def dashboard():
    df = fetch_sales()
    summary = build_summary(df)
    products = build_product_ranking(df)
    monthly = build_monthly_trend(df)
    create_charts(df, Path("static") / "charts")
    return render_template(
        "dashboard.html",
        summary=summary,
        products=products.to_dict("records"),
        monthly=monthly.to_dict("records"),
        has_data=not df.empty,
        required_columns=", ".join(REQUIRED_COLUMNS),
    )

@app.route("/upload", methods=["POST"])
def upload_csv():
    uploaded = request.files.get("file")
    if not uploaded or not uploaded.filename:
        flash("Choose a CSV file before uploading.", "error")
        return redirect(url_for("dashboard"))

    filename = secure_filename(uploaded.filename)
    if not filename.lower().endswith(".csv"):
        flash("Only .csv files are supported.", "error")
        return redirect(url_for("dashboard"))

    saved_path = Path(app.config["UPLOAD_FOLDER"]) / filename
    uploaded.save(saved_path)

    try:
        cleaned, errors = validate_and_clean_csv(saved_path)
        report_path = Path(app.config["REPORT_FOLDER"]) / "csv_validation_report.csv"
        pd.DataFrame(errors, columns=["row_number", "error"]).to_csv(report_path, index=False)

        # inserted, duplicates = insert_sales(cleaned)
        # flash(
        #     f"Import finished: {inserted} row(s) imported, {duplicates} exact duplicate row(s) skipped, "
        #     f"{len(errors)} invalid row(s) reported.",
        #     "success" if not errors else "warning",
        # )
        # flash("Validation report saved to reports/csv_validation_report.csv.", "info")
    except Exception as exc:
        flash(f"Could not process the CSV: {exc}", "error")
    return redirect(url_for("dashboard"))

@app.route("/report")
def download_report():
    path = Path(app.config["REPORT_FOLDER"]) / "csv_validation_report.csv"
    if not path.exists():
        pd.DataFrame([], columns=["row_number", "error"]).to_csv(path, index=False)
    return send_file(path, as_attachment=True, download_name="csv_validation_report.csv")

@app.route("/sales.csv")
def export_sales():
    df = fetch_sales()
    path = Path(app.config["REPORT_FOLDER"]) / "sales_export.csv"
    df.to_csv(path, index=False)
    return send_file(path, as_attachment=True, download_name="sales_export.csv")

if __name__ == "__main__":
    init_db()
    app.config["DB_INITIALIZED"] = True
    app.run(debug=True)
