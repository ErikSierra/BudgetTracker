import os
import shutil
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
            **{
                "Description": "Description",
                "Category": "Category",
                "Amount (USD)": "Amount",
                "Amount": "Amount"
            }
        }
    elif file_name.startswith("Discover"):
        source_label = "Discover Card"
        column_mapping = {
            "Trans. Date": "TransactionDate",
            "Post Date": "ClearingDate",
            **{
                "Description": "Description",
                "Category": "Category",
                "Amount (USD)": "Amount",
                "Amount": "Amount"
            }
        }
    else:
        raise ValueError("Invalid file type, does not start with 'Apple Card' or 'Discover'")

    # Rename columns and convert dates with error handling
    df = df.rename(columns=column_mapping)
    df["TransactionDate"] = pd.to_datetime(df["TransactionDate"], errors='coerce').dt.date
    df["ClearingDate"] = pd.to_datetime(df["ClearingDate"], errors='coerce').dt.date
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
    # Directories for source, archive, and logs
    source_folder = r"C:\Coding Stuff\Python Projects\AzureSQLdb\DataStorage"
    archive_folder = r"C:\Coding Stuff\Python Projects\AzureSQLdb\DataStorage\Archive"
    log_folder = r"C:\Coding Stuff\Python Projects\AzureSQLdb\Logs\AzureBudgetLoader logs"

    # Create archive and log folders if they don't exist
    os.makedirs(archive_folder, exist_ok=True)
    os.makedirs(log_folder, exist_ok=True)

    # Create a new log file with a timestamp in its name
    log_file = os.path.join(log_folder, f"process_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

    # Setup logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    # Database connection details
    server = "sierra.database.windows.net"
    database = "Sierra"
    username = "CloudSA3e269270"
    password = "BuildLegos77"
    driver = "{ODBC Driver 17 for SQL Server}"
    connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"

    # List all CSV files in the source folder (case-insensitive)
    csv_files = [f for f in os.listdir(source_folder) if f.lower().endswith('.csv')]

    if not csv_files:
        logging.info("No files to process.")
        return

    try:
        with pyodbc.connect(connection_string) as conn:
            logging.info("Database connection established successfully.")
            for file_name in csv_files:
                file_path = os.path.join(source_folder, file_name)
                try:
                    # Load the CSV file
                    df = pd.read_csv(file_path, dtype={'Amount (USD)': float})
                    # Preprocess data based on the file type
                    df = preprocess_data(df, file_name)
                    # Insert data into the SQL table in batch
                    insert_data_to_sql(df, conn)
                    logging.info(f"Data successfully inserted from {file_name} into BudgetTracker.")

                    # Move the processed file to the archive folder
                    archive_path = os.path.join(archive_folder, file_name)
                    shutil.move(file_path, archive_path)
                    logging.info(f"Moved {file_name} to archive.")
                except Exception as e:
                    logging.exception(f"Error processing file {file_name}: {e}")
                    continue
    except Exception as e:
        logging.exception(f"Error connecting to the database: {e}")


if __name__ == "__main__":
    main()