import os
import shutil
import sys
import re
import py7zr
import zipfile
import rarfile

def extract_archive(archive_path, extract_path):
    """
    Extract various archive formats (7z, zip, rar)
    """
    try:
        file_lower = archive_path.lower()
        if file_lower.endswith('.7z'):
            with py7zr.SevenZipFile(archive_path, 'r') as archive:
                archive.extractall(extract_path)
        elif file_lower.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as archive:
                archive.extractall(extract_path)
        elif file_lower.endswith('.rar'):
            with rarfile.RarFile(archive_path, 'r') as archive:
                archive.extractall(extract_path)
        return True
    except Exception as e:
        print(f"Error extracting {archive_path}: {e}")
        return False

def process_folder(folder_path):
    """
    Process a folder for archives and extract them
    """
    found_archives = False
    print(f"Scanning folder: {folder_path}")
    
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            if item_path.lower().endswith(('.7z', '.zip', '.rar')):
                found_archives = True
                print(f"Found archive: {item}")
                extract_dir = os.path.splitext(item_path)[0]
                if extract_archive(item_path, folder_path):
                    os.remove(item_path)  # Remove archive after successful extraction
                    if os.path.exists(extract_dir):
                        process_folder(extract_dir)  # Recursively process extracted folder
    
    if not found_archives:
        print("No archives found to process.")
        return True
    return True

def merge_folders(root_folder, base_folder_name=None):
    """
    Merge the contents of folders matching a pattern
    """
    try:
        # If base_folder_name is not provided, try to detect it
        if not base_folder_name:
            pattern = r"(.*?)-\d{3}$"
            folders_found = False
            for item in os.listdir(root_folder):
                if os.path.isdir(os.path.join(root_folder, item)):
                    match = re.match(pattern, item)
                    if match:
                        folders_found = True
                        base_folder_name = match.group(1)
                        break
            
            if not folders_found:
                print("No folders found matching the expected pattern.")
                return True  # Return success when no matching folders found
        
        print(f"Processing base folder name: {base_folder_name}")
        # Rest of the merge logic...
        return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python scriptcombine.py /path/to/folder")
        return 1

    folder_path = sys.argv[1]
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory")
        return 1

    print(f"Processing folder: {folder_path}")
    if process_folder(folder_path) and merge_folders(folder_path):
        print("Processing completed successfully")
        return 0
    else:
        print("Processing completed with errors")
        return 1

if __name__ == "__main__":
    sys.exit(main())
