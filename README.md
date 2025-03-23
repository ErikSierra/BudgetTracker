# 💰 BudgetTracker

**BudgetTracker** is a Python automation tool that ingests and processes credit card transactions from CSV files, standardizes the data, and uploads it into an Azure SQL database for easy tracking and analysis.

---

## 🚀 Features

- Supports Apple Card, Discover, and 5/3 Bank CSV formats
- Cleans and normalizes inconsistent columns and date formats
- Inserts data into an Azure-hosted SQL Server table
- Uses Azure Key Vault for secure credential storage
- Automatically archives processed files
- Logs all activity for transparency and troubleshooting

---

## 🧰 Tech Stack

- Python • Pandas • pyodbc  
- Azure SQL • Azure Key Vault  
- Power BI (optional for visualization)

---

## 📁 Main Scripts

- `azure_budget_loader.py` — Main script for new transaction ingestion
- `recovery_loader.py` — Reprocesses archived files if needed

---

## 📊 Optional: Power BI Dashboard

Connect your Azure SQL database to Power BI to visualize:
- Spending trends
- Category breakdowns
- Source-specific summaries
