import os
import time
import logging

def delete_old_logs(folder_paths, days=15):
    # Calculate the cutoff time in seconds since the epoch
    cutoff = time.time() - days * 24 * 3600
    for folder in folder_paths:
        if not os.path.exists(folder):
            logging.info(f"Folder does not exist: {folder}")
            continue

        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                file_mod_time = os.path.getmtime(file_path)
                if file_mod_time < cutoff:
                    try:
                        os.remove(file_path)
                        logging.info(f"Deleted file: {file_path}")
                    except Exception as e:
                        logging.error(f"Error deleting file {file_path}: {e}")

def main():
    # Specify the two log folder paths
    log_folders = [
        r"C:\Coding Stuff\Python Projects\AzureSQLdb\Logs\AzureBudgetLoader logs",
        r"C:\Coding Stuff\Python Projects\AzureSQLdb\Logs\DataTransport logs"
    ]

    # Setup logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    delete_old_logs(log_folders, days=15)

if __name__ == "__main__":
    main()
