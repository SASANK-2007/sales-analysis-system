# Sales Data Analysis System

A beginner-friendly Flask + MySQL web application that imports sales CSV files, validates rows, calculates revenue and quantities, ranks products, and displays monthly sales charts.

## Features

- Upload and validate structured CSV files.
- Check required columns and report malformed rows.
- Store products and sales in MySQL.
- Calculate revenue (`quantity × unit_price`) and total quantity sold.
- Rank products by quantity sold and show monthly trends.
- Generate monthly line and top-products bar charts with Matplotlib.
- Download the CSV validation/error report and export accepted sales.
- Prevent exact duplicate imports with a SHA-256 fingerprint.

## Folder structure

```text
sales-data-analysis-system/
├── app.py
├── analysis.py
├── config.py
├── csv_service.py
├── database.py
├── schema.sql
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   ├── base.html
│   └── dashboard.html
├── static/
│   ├── style.css
│   └── sample_sales.csv
├── uploads/
│   └── .gitkeep
├── reports/
│   └── .gitkeep
└── tests/
    └── test_csv_service.py
```

## Requirements

- Python 3.10 or newer
- MySQL Server 8.x (or compatible MySQL server)
- Git (only needed for publishing to GitHub)

## Run on Windows

### 1. Extract and open the project

Extract the ZIP, then open the `sales-data-analysis-system` folder in VS Code or a terminal.

### 2. Create and activate a virtual environment

PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

### 3. Install Python dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Set up MySQL

Start the MySQL service. Create a MySQL user/database if you do not want to use `root`.

PowerShell example (replace the password with your actual MySQL password):

```powershell
$env:DB_HOST="localhost"
$env:DB_PORT="3306"
$env:DB_USER="root"
$env:DB_PASSWORD="YOUR_MYSQL_PASSWORD"
$env:DB_NAME="sales_analysis"
$env:SECRET_KEY="replace-with-a-long-random-secret"
```

Command Prompt example:

```bat
set DB_HOST=localhost
set DB_PORT=3306
set DB_USER=root
set DB_PASSWORD=YOUR_MYSQL_PASSWORD
set DB_NAME=sales_analysis
set SECRET_KEY=replace-with-a-long-random-secret
```

The app creates the database and tables automatically when it starts. You can also run `schema.sql` in MySQL Workbench first. Do not commit real passwords to Git.

### 5. Start the application

```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

### 6. Try the sample CSV

Click **Download sample CSV**, then upload the file back into the app. You should see revenue, quantity, product rankings, and monthly charts.

## CSV format

The CSV must contain these column names (case-insensitive; surrounding whitespace is ignored):

```csv
sale_date,product_name,category,quantity,unit_price,region
2026-01-05,Notebook,Stationery,20,45.00,South
```

Validation rules:
- `sale_date` must be a valid date.
- `product_name`, `category`, and `region` cannot be empty.
- `quantity` must be a positive integer.
- `unit_price` must be a non-negative finite number.
- Rows that fail validation are skipped and listed in `reports/csv_validation_report.csv`.
- Missing required columns stop the import and show an error.

## Duplicate import policy

The application computes a SHA-256 hash over normalized `product_name`, `category`, `sale_date`, `quantity`, `unit_price` (rounded to 2 decimals), and `region`. Exact matching rows are stored only once across all imports. This is suitable for a beginner project, but it can also classify two legitimate, identical-looking transactions as duplicates. In a production system, use a unique transaction ID supplied by the source system.

## Run tests

```bash
python -m unittest discover -s tests -v
```

The tests cover required-column validation and malformed row handling.

## Push the project to GitHub

1. Create a new **empty** repository on GitHub. Do not add a README if you already have one locally.
2. Open a terminal in the project folder.
3. Run:

```bash
git init
git add .
git commit -m "Build Sales Data Analysis System"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/sales-data-analysis-system.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username and use your actual repository URL.

If Git asks you to identify yourself, configure your Git identity:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Then repeat the commit. For GitHub HTTPS authentication, use the browser sign-in flow or a personal access token when prompted; your GitHub account password is not accepted for Git operations.

### If a remote already exists

Check it:

```bash
git remote -v
```

Update it if necessary:

```bash
git remote set-url origin https://github.com/YOUR-USERNAME/sales-data-analysis-system.git
```

Then push:

```bash
git push -u origin main
```

## Troubleshooting

- **Access denied for MySQL**: verify `DB_USER` and `DB_PASSWORD`, and make sure MySQL is running.
- **Can't connect to MySQL**: verify the host and port; the common local port is `3306`.
- **No module named ...**: activate `.venv` and run `pip install -r requirements.txt`.
- **Port 5000 is busy**: stop the other process or change the port in `app.run(port=5001)`.
- **Charts do not show**: upload a valid CSV and refresh the dashboard.
