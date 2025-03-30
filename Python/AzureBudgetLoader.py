import concurrent.futures
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
        self.source_folder = r"C:\Coding Stuff\Python Projects\AzureSQLdb\DataStorage"
        self.archive_folder = os.path.join(self.source_folder, "Archive")
        self.log_folder = r"C:\Coding Stuff\Python Projects\AzureSQLdb\Logs\AzureBudgetLoader logs"

        os.makedirs(self.archive_folder, exist_ok=True)
        os.makedirs(self.log_folder, exist_ok=True)

        log_file = os.path.join(self.log_folder, f"process_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
        )

        self.credential = DefaultAzureCredential()
        self.vault_url = "https://Esierra.vault.azure.net"
        self.client = SecretClient(vault_url=self.vault_url, credential=self.credential)

        # Define a file size threshold (in bytes) to consider a file "large"
        self.large_file_threshold = 10 * 1024 * 1024  # 10 MB threshold
        # Define a chunksize for processing large CSV files
        self.csv_chunksize = 100000

    def get_db_connection(self):
        try:
            server = self.client.get_secret("sql-server").value
            database = self.client.get_secret("sql-database").value
            username = self.client.get_secret("sql-username").value
            password = self.client.get_secret("sql-password").value
            driver = "{ODBC Driver 17 for SQL Server}"
            conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
            return pyodbc.connect(conn_str)
        except Exception as e:
            logging.exception("Failed to retrieve secrets or connect to SQL server.")
            raise

    def process_file(self, file_name):
        file_path = os.path.join(self.source_folder, file_name)
        try:
            file_size = os.path.getsize(file_path)
            processor = TransactionProcessor(file_name)
            if file_size > self.large_file_threshold:
                logging.info(f"File {file_name} is large ({file_size} bytes), processing in chunks.")
                chunks = []
                for chunk in pd.read_csv(file_path, chunksize=self.csv_chunksize):
                    processed_chunk = processor.preprocess(chunk)
                    chunks.append(processed_chunk)
                processed_df = pd.concat(chunks, ignore_index=True)
            else:
                df = pd.read_csv(file_path)
                processed_df = processor.preprocess(df)
            logging.info(f"Processed {file_name} with {len(processed_df)} rows.")
            return processed_df, file_name
        except Exception as e:
            logging.exception(f"Error processing file {file_name}: {e}")
            return None

    def run(self):
        csv_files = [f for f in os.listdir(self.source_folder) if f.lower().endswith('.csv')]
        if not csv_files:
            logging.info("No CSV files found for processing.")
            return

        processed_results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.process_file, file_name): file_name for file_name in csv_files}
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result is not None:
                    processed_results.append(result)

        if not processed_results:
            logging.info("No files processed successfully.")
            return

        # Combine all processed DataFrames for a single bulk insertion.
        all_data = pd.concat([df for df, fname in processed_results], ignore_index=True)

        try:
            with self.get_db_connection() as conn:
                uploader = SQLUploader(conn)
                uploader.insert_data(all_data)
                logging.info(f"Inserted {len(all_data)} rows from {len(processed_results)} files into BudgetTracker.")
        except Exception as e:
            logging.exception("Critical failure during batch insertion.")
            return

        # Archive successfully processed files.
        for _, file_name in processed_results:
            file_path = os.path.join(self.source_folder, file_name)
            archive_path = os.path.join(self.archive_folder, file_name)
            try:
                shutil.move(file_path, archive_path)
                logging.info(f"Archived file: {file_name}")
            except Exception as e:
                logging.exception(f"Error archiving file {file_name}: {e}")

if __name__ == "__main__":
    app = BudgetLoaderApp()
    app.run()
