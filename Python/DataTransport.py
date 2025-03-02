import os
import shutil
import logging
from datetime import datetime


def main():
    # Directories for source, destination, and logs
    downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
    destination_folder = r"C:\Coding Stuff\Python Projects\AzureSQLdb\DataStorage"
    log_folder = r"C:\Coding Stuff\Python Projects\AzureSQLdb\Logs\DataTransport logs"

    # Create log and destination folders if they don't exist
    os.makedirs(log_folder, exist_ok=True)
    os.makedirs(destination_folder, exist_ok=True)

    # Create a new log file with a timestamp in its name
    log_file = os.path.join(log_folder, f"move_files_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

    # Setup logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    files_moved = 0

    # List and move eligible CSV files from Downloads
    for file_name in os.listdir(downloads_folder):
        if file_name.lower().endswith('.csv') and (
                file_name.startswith('Apple Card') or file_name.startswith('Discover') or file_name.startswith('EXPORT')):

            source_path = os.path.join(downloads_folder, file_name)
            destination_path = os.path.join(destination_folder, file_name)

            try:
                shutil.move(source_path, destination_path)
                logging.info(f"Moved: {file_name}")
                files_moved += 1
            except Exception as e:
                logging.error(f"Error moving {file_name}: {e}")

    if files_moved == 0:
        logging.info("No files to move.")


if __name__ == "__main__":
    main()
