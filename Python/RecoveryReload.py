import os
import pandas as pd
import pyodbc
import logging
from datetime import datetime


def preprocess_data(df, file_name):
    if file_name.startswith("Apple Card"):
        source_label = "Apple Card"
        column_mapping = {
            "Transaction Date": "TransactionDate",
            "Clearing Date": "ClearingDate",
            "Description": "Description",
            "Category": "Category",
            "Amount (USD)": "Amount",
            "Amount": "Amount"
        }
    elif file_name.startswith("Discover"):
        source_label = "Discover Card"
        column_mapping = {
            "Trans. Date": "TransactionDate",
            "Post Date": "ClearingDate",
            "Description": "Description",
            "Category": "Category",
            "Amount (USD)": "Amount",
            "Amount": "Amount"
        }
    elif file_name.startswith("EXPORT"):
        source_label = "5/3 Bank"
        column_mapping = {
            "Date": "TransactionDate",
            "Description": "Description",
            "Amount": "Amount"
        }
        df["ClearingDate"] = None
        df["Category"] = None
    else:
        raise ValueError(f"Invalid file type: {file_name}. Must start with 'Apple Card', 'Discover', or 'EXPORT'.")

    df = df.rename(columns=column_mapping)

    required_columns = ["TransactionDate", "ClearingDate", "Description", "Category", "Amount"]
    for col in required_columns:
        if col not in df.columns:
            df[col] = None

    df["TransactionDate"] = pd.to_datetime(df["TransactionDate"], errors='coerce').dt.date
    df["ClearingDate"] = pd.to_datetime(df["ClearingDate"], errors='coerce').dt.date
    df["Amount"] = pd.to_numeric(df["Amount"], errors='coerce').fillna(0)
    df["Source"] = source_label

    return df


def insert_data_to_sql(df, conn):
    with conn.cursor() as cursor:
        cursor.fast_executemany = True
        insert_query = """
            INSERT INTO BudgetTracker (TransactionDate, ClearingDate, Description, Category, Amount, Source)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        data = df[['TransactionDate', 'ClearingDate', 'Description', 'Category', 'Amount', 'Source']].values.tolist()
        cursor.executemany(insert_query, data)
        conn.commit()


def main():
    archive_folder = r"C:\DummyPath\DataStorage\Archive"
    log_folder = r"C:\DummyPath\Logs"

    os.makedirs(log_folder, exist_ok=True)

    log_file = os.path.join(log_folder, f"recovery_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
    )

    server = "dummyserver.database.windows.net"
    database = "DummyDatabase"
    username = "dummyuser"
    password = "DummyPassword123!"
    driver = "{ODBC Driver 17 for SQL Server}"
    connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"

    csv_files = [f for f in os.listdir(archive_folder) if f.lower().endswith('.csv')]

    if not csv_files:
        logging.info("No archived CSV files found for recovery.")
        return

    try:
        with pyodbc.connect(connection_string) as conn:
            logging.info("Database connection established successfully for recovery.")

            for file_name in sorted(csv_files):  # sorted ensures oldest files processed first
                file_path = os.path.join(archive_folder, file_name)

                try:
                    df = pd.read_csv(file_path)
                    df = preprocess_data(df, file_name)
                    insert_data_to_sql(df, conn)
                    logging.info(f"Inserted {len(df)} rows from {file_name} into BudgetTracker.")
                except Exception as e:
                    logging.exception(f"Error processing archived file {file_name}: {e}")
                    continue
    except pyodbc.Error as e:
        logging.exception(f"Database connection error during recovery: {e}")


if __name__ == "__main__":
    main()
