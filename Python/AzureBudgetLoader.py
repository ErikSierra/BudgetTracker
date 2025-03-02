import os
import shutil
import pandas as pd
import pyodbc
import logging
from datetime import datetime


def preprocess_data(df, file_name):
    """
    Preprocess CSV data based on file name prefix.
    """
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
        # EXPORT files lack ClearingDate & Category, so fill them with NULLs
        df["ClearingDate"] = None
        df["Category"] = None
    else:
        raise ValueError(f"Invalid file type: {file_name}. Must start with 'Apple Card', 'Discover', or 'EXPORT'.")

    # Rename columns
    df = df.rename(columns=column_mapping)

    # Ensure required columns exist and fill missing ones with None
    required_columns = ["TransactionDate", "ClearingDate", "Description", "Category", "Amount"]
    for col in required_columns:
        if col not in df.columns:
            df[col] = None  # Assign NULL equivalent

    # Convert date columns safely
    df["TransactionDate"] = pd.to_datetime(df["TransactionDate"], errors='coerce').dt.date
    df["ClearingDate"] = pd.to_datetime(df["ClearingDate"], errors='coerce').dt.date

    # Convert amount to numeric (set to 0 if conversion fails)
    df["Amount"] = pd.to_numeric(df["Amount"], errors='coerce').fillna(0)

    # Assign source
    df["Source"] = source_label

    return df


def insert_data_to_sql(df, conn):
    """
    Insert processed data into SQL database.
    """
    with conn.cursor() as cursor:
        cursor.fast_executemany = True  # Optimized for batch inserts

        insert_query = """
            INSERT INTO BudgetTracker (TransactionDate, ClearingDate, Description, Category, Amount, Source)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        data = df[['TransactionDate', 'ClearingDate', 'Description', 'Category', 'Amount', 'Source']].values.tolist()

        cursor.executemany(insert_query, data)
        conn.commit()


def main():
    """
    Main script execution.
    """
    # Directories
    source_folder = r"C:\Coding Stuff\Python Projects\AzureSQLdb\DataStorage"
    archive_folder = r"C:\Coding Stuff\Python Projects\AzureSQLdb\DataStorage\Archive"
    log_folder = r"C:\Coding Stuff\Python Projects\AzureSQLdb\Logs\AzureBudgetLoader logs"

    os.makedirs(archive_folder, exist_ok=True)
    os.makedirs(log_folder, exist_ok=True)

    # Setup logging
    log_file = os.path.join(log_folder, f"process_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
    )

    # Database connection details
    server = "sierra.database.windows.net"
    database = "Sierra"
    username = "CloudSA3e269270"
    password = "BuildLegos77"
    driver = "{ODBC Driver 17 for SQL Server}"
    connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"

    # Find CSV files in the folder
    csv_files = [f for f in os.listdir(source_folder) if f.lower().endswith('.csv')]

    if not csv_files:
        logging.info("No CSV files found for processing.")
        return

    try:
        with pyodbc.connect(connection_string) as conn:
            logging.info("Database connection established successfully.")

            for file_name in csv_files:
                file_path = os.path.join(source_folder, file_name)
                archive_path = os.path.join(archive_folder, file_name)

                try:
                    # Load CSV file
                    df = pd.read_csv(file_path)

                    # Process the data
                    df = preprocess_data(df, file_name)

                    # Insert into SQL
                    insert_data_to_sql(df, conn)
                    logging.info(f"Inserted {len(df)} rows from {file_name} into BudgetTracker.")

                    # Move file to archive
                    shutil.move(file_path, archive_path)
                    logging.info(f"Moved {file_name} to archive.")

                except Exception as e:
                    logging.exception(f"Error processing file {file_name}: {e}")
                    continue
    except pyodbc.Error as e:
        logging.exception(f"Database connection error: {e}")


if __name__ == "__main__":
    main()
