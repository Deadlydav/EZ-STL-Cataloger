import os
import py7zr
import sys
import traceback

def test_py7zr():
    """Test if py7zr is working properly"""
    print("Testing py7zr installation...")
    try:
        print(f"py7zr version: {py7zr.__version__}")
        return True
    except Exception as e:
        print(f"Error with py7zr: {e}")
        return False

def extract_7z_and_delete(file_path):
    """Extract a .7z file and delete it after successful extraction"""
    try:
        # Create extraction directory
        extract_to = os.path.join(os.path.dirname(file_path), 
                                os.path.splitext(os.path.basename(file_path))[0])
        os.makedirs(extract_to, exist_ok=True)

        # Extract the archive
        print(f"Extracting: {file_path} -> {extract_to}")
        with py7zr.SevenZipFile(file_path, mode='r') as z:
            z.extractall(path=extract_to)
        
        # Delete the original archive
        os.remove(file_path)
        print(f"Successfully extracted and deleted: {file_path}")
        return True
    except Exception as e:
        print(f"Error processing {file_path}:")
        print(traceback.format_exc())
        return False

def process_7z_folder(folder_path):
    """Process all .7z files in a folder and its subfolders"""
    if not os.path.exists(folder_path):
        print(f"Error: Folder does not exist: {folder_path}")
        return False

    print(f"Processing folder: {folder_path}")
    found_files = False
    success = True
    
    try:
        print(f"Scanning for .7z files in: {folder_path}")
        for root, dirs, files in os.walk(folder_path):
            print(f"Checking directory: {root}")
            for file in files:
                print(f"Found file: {file}")
                if file.lower().endswith('.7z'):
                    found_files = True
                    file_path = os.path.join(root, file)
                    print(f"Found .7z file: {file_path}")
                    if not extract_7z_and_delete(file_path):
                        success = False
        
        if not found_files:
            print("\nNo .7z files found in the specified folder.")
            print("Make sure you have .7z files in the folder and try again.")
            return True  # Return success when no files found
            
    except Exception as e:
        print(f"Error walking through folder {folder_path}:")
        print(traceback.format_exc())
        success = False
    
    return success

def main():
    # Test py7zr first
    if not test_py7zr():
        print("py7zr test failed. Please reinstall the package.")
        return 1

    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python script7zextract.py <folder_path>")
        return 1

    folder_path = sys.argv[1]
    
    # Verify folder exists
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory")
        return 1

    # Process the folder
    print(f"Starting to process folder: {folder_path}")
    success = process_7z_folder(folder_path)
    
    if success:
        print("Processing completed successfully")
        return 0
    else:
        print("Processing completed with errors")
        return 1

if __name__ == "__main__":
    sys.exit(main())
