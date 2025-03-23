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

![image](https://github.com/user-attachments/assets/8914a389-5347-42b0-8a35-f6262d8a0590)
![image](https://github.com/user-attachments/assets/48eacdc5-ee24-4f50-96fe-52b794baec62)


