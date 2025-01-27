import os
import sys

def count_images_in_folder(folder_path):
    """Count the number of image files in a folder"""
    image_count = 0
    for item in os.listdir(folder_path):
        if item.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
            image_count += 1
    return image_count

def is_folder_empty_or_images_only(folder_path, min_images=3, delete_mode="all"):
    """
    Check folder contents based on specified criteria
    
    Args:
        folder_path: Path to the folder
        min_images: Minimum number of images required to keep folder
        delete_mode: 
            "all" - Delete folders with only images
            "few" - Delete folders with fewer than min_images
            "keep" - Keep images, delete empty folders only
    """
    try:
        has_non_image = False
        has_model = False
        image_count = 0
        
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                if item.lower().endswith(('.stl', '.obj')):
                    has_model = True
                    return False
                elif item.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
                    image_count += 1
                else:
                    has_non_image = True
            elif os.path.isdir(item_path):
                if not is_folder_empty_or_images_only(item_path, min_images, delete_mode):
                    return False

        if has_model:
            return False
        
        if delete_mode == "all":
            return not has_non_image
        elif delete_mode == "few":
            return not has_non_image and image_count < min_images
        elif delete_mode == "keep":
            return not has_non_image and image_count == 0
        
        return False
    except Exception as e:
        print(f"Error checking folder {folder_path}: {e}")
        return False

def delete_empty_folders(start_path, min_images=3, delete_mode="all"):
    """Delete folders based on specified criteria"""
    print(f"Scanning: {start_path}")
    print(f"Mode: {delete_mode}, Minimum images: {min_images}")
    folders_deleted = 0
    
    for root, dirs, files in os.walk(start_path, topdown=False):
        for dir_name in dirs:
            folder_path = os.path.join(root, dir_name)
            
            try:
                if is_folder_empty_or_images_only(folder_path, min_images, delete_mode):
                    print(f"\nFound folder matching criteria: {folder_path}")
                    image_count = count_images_in_folder(folder_path)
                    print(f"Images in folder: {image_count}")
                    
                    while True:
                        response = input(f"Delete this folder and its contents? (y/n): ").lower().strip()
                        if response in ['y', 'n']:
                            break
                        print("Please enter 'y' for yes or 'n' for no.")
                    
                    if response == 'y':
                        # Delete all files in the folder first
                        for file in os.listdir(folder_path):
                            file_path = os.path.join(folder_path, file)
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                                print(f"Deleted file: {file_path}")
                        # Then delete the folder
                        os.rmdir(folder_path)
                        print(f"Deleted folder: {folder_path}")
                        folders_deleted += 1
                    else:
                        print(f"Skipped folder: {folder_path}")
            except Exception as e:
                print(f"Error processing {folder_path}: {e}")
                continue

    print(f"\nTotal folders deleted: {folders_deleted}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python scriptdeletempty.py <folder_path> [min_images] [delete_mode]")
        print("Delete modes:")
        print("  all  - Delete folders with only images (default)")
        print("  few  - Delete folders with fewer than min_images")
        print("  keep - Keep images, delete empty folders only")
        return 1

    folder_path = ' '.join(sys.argv[1:-2] if len(sys.argv) > 3 else [sys.argv[1]])
    folder_path = folder_path.strip('"\'')
    folder_path = os.path.abspath(folder_path)

    min_images = 3
    delete_mode = "all"

    if len(sys.argv) > 2:
        try:
            min_images = int(sys.argv[-2])
        except ValueError:
            delete_mode = sys.argv[-2]
    
    if len(sys.argv) > 3:
        delete_mode = sys.argv[-1]

    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory")
        return 1

    delete_empty_folders(folder_path, min_images, delete_mode)
    return 0

if __name__ == "__main__":
    sys.exit(main())
