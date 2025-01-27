import os
import zipfile
import tarfile
import subprocess
from concurrent.futures import ThreadPoolExecutor
import sys

# Function to extract and delete a compressed file
def extract_and_delete(file_path):
    extract_to = os.path.join(os.path.dirname(file_path), os.path.splitext(os.path.basename(file_path))[0])
    os.makedirs(extract_to, exist_ok=True)  # Create output folder if it doesn't exist
    try:
        if file_path.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        elif file_path.endswith(('.tar.gz', '.tgz', '.tar')):
            with tarfile.open(file_path, 'r:*') as tar_ref:
                tar_ref.extractall(extract_to)
        elif file_path.endswith('.rar'):
            # Use WinRAR command-line tool
            winrar_path = r"C:\Program Files\WinRAR\WinRAR.exe"  # Adjust the path if necessary
            subprocess.run([winrar_path, "x", "-y", file_path, extract_to], check=True)
        else:
            print(f"Unsupported file type: {file_path}")
            return
        print(f"Extracted: {file_path} -> {extract_to}")
        os.remove(file_path)  # Delete the compressed file after extraction
        print(f"Deleted: {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# Recursive function to scan and extract files
def process_folder(folder_path, executor):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(('.zip', '.tar.gz', '.tgz', '.tar', '.rar')):
                # Submit the extraction task to the thread pool
                executor.submit(extract_and_delete, file_path)

# Path to the main folder
main_folder = r"D:\STLPROCESSIOR"

# Start processing
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scriptunzipmultirar.py /path/to/folder")
        sys.exit(1)

    folder_path = sys.argv[1]
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory")
        sys.exit(1)

    MAX_THREADS = 3
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        process_folder(folder_path, executor)
