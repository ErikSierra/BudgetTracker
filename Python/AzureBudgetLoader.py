import logging
import os
import shutil
import pandas as pd
import pyodbc
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

class TransactionProcessor:
    def __init__(self, file_name):
        self.file_name = file_name
        self.source_label = None

    def preprocess(self, df):
        if self.file_name.startswith("Apple Card"):
            self.source_label = "Apple Card"
            column_mapping = {
                "Transaction Date": "TransactionDate",
                "Clearing Date": "ClearingDate",
                "Description": "Description",
                "Category": "Category",
                "Amount (USD)": "Amount",
                "Amount": "Amount"
            }
        elif self.file_name.startswith("Discover"):
            self.source_label = "Discover Card"
            column_mapping = {
                "Trans. Date": "TransactionDate",
                "Post Date": "ClearingDate",
                "Description": "Description",
                "Category": "Category",
                "Amount (USD)": "Amount",
                "Amount": "Amount"
            }
        elif self.file_name.startswith("EXPORT"):
            self.source_label = "5/3 Bank"
            column_mapping = {
                "Date": "TransactionDate",
                "Description": "Description",
                "Amount": "Amount"
            }
            df["ClearingDate"] = None
            df["Category"] = None
        else:
            raise ValueError(f"Invalid file type: {self.file_name}")

        df = df.rename(columns=column_mapping)

        for col in ["TransactionDate", "ClearingDate", "Description", "Category", "Amount"]:
            if col not in df.columns:
                df[col] = None

        df["TransactionDate"] = pd.to_datetime(df["TransactionDate"], errors='coerce').dt.date
        df["ClearingDate"] = pd.to_datetime(df["ClearingDate"], errors='coerce').dt.date
        df["Amount"] = pd.to_numeric(df["Amount"], errors='coerce').fillna(0)
        df["Source"] = self.source_label

        return df[["TransactionDate", "ClearingDate", "Description", "Category", "Amount", "Source"]]


class SQLUploader:
    def __init__(self, connection):
        self.connection = connection

    def insert_data(self, df):
        with self.connection.cursor() as cursor:
            cursor.fast_executemany = True
            insert_query = """
                INSERT INTO BudgetTracker (TransactionDate, ClearingDate, Description, Category, Amount, Source)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            data = df.values.tolist()
            cursor.executemany(insert_query, data)
            self.connection.commit()


class BudgetLoaderApp:
    def __init__(self):
        self.source_folder = r"C:\DummyPath\DataStorage"
        self.archive_folder = os.path.join(self.source_folder, "Archive")
        self.log_folder = r"C:\DummyPath\Logs"

        os.makedirs(self.archive_folder, exist_ok=True)
        os.makedirs(self.log_folder, exist_ok=True)

        log_file = os.path.join(self.log_folder, f"process_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
        )

        self.credential = DefaultAzureCredential()
        self.vault_url = "https://DummyVaultName.vault.azure.net"
        self.client = SecretClient(vault_url=self.vault_url, credential=self.credential)

    def get_db_connection(self):
        try:
            server = self.client.get_secret("dummy-sql-server").value
            database = self.client.get_secret("dummy-sql-database").value
            username = self.client.get_secret("dummy-sql-username").value
            password = self.client.get_secret("dummy-sql-password").value
            driver = "{ODBC Driver 17 for SQL Server}"
            conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
            return pyodbc.connect(conn_str)
        except Exception as e:
            logging.exception("Failed to retrieve secrets or connect to SQL server.")
            raise

    def run(self):
        csv_files = [f for f in os.listdir(self.source_folder) if f.lower().endswith('.csv')]
        if not csv_files:
            logging.info("No CSV files found for processing.")
            return

        try:
            with self.get_db_connection() as conn:
                uploader = SQLUploader(conn)
                for file_name in csv_files:
                    file_path = os.path.join(self.source_folder, file_name)
                    archive_path = os.path.join(self.archive_folder, file_name)
                    try:
                        df = pd.read_csv(file_path)
                        processor = TransactionProcessor(file_name)
                        processed_df = processor.preprocess(df)
                        uploader.insert_data(processed_df)
                        logging.info(f"Inserted {len(processed_df)} rows from {file_name} into BudgetTracker.")
                        shutil.move(file_path, archive_path)
                        logging.info(f"Archived file: {file_name}")
                    except Exception as e:
                        logging.exception(f"Error processing file {file_name}: {e}")
                        continue
        except Exception as e:
            logging.exception("Critical failure during processing.")


if __name__ == "__main__":
    app = BudgetLoaderApp()
    app.run()
