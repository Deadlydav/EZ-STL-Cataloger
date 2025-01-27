# EZ-STL-Cataloger
Simplify 3D model organization with EZ STL Cataloger! Extract and organize your files, create stunning top/front view images of STL/OBJ models, and clean up your folders in a few clicks. Designed for 3D printing enthusiasts and professionals

## Features
- **Batch processing** of STL and OBJ files
- **Top and front view previews** of 3D models (saved as PNG images)
- Automatic extraction of **RAR**, **ZIP**, and **7z** archives
- **Folder cleanup**: Deletes empty or unwanted folders
- **Combines and organizes** scattered files for easy cataloging
- User-friendly **GUI** for effortless operation

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Deadlydav/EZ-STL-Cataloger.git
   cd EZ-STL-Cataloger
2. Install dependencies:
   ```bash
    python installation.py
  This script checks your Python version, installs required libraries, and validates dependencies.

 4. (Optional) If installation.py does not run correctly, manually install dependencies:
     ```bash
    pip install -r requirements.txt
     
Usage

    python main.py

make sure all the other script are in the same document a .exe or individual script is on the way
  
  Using the GUI
  1. Input Folder Selection: Browse and select the folder containing STL/OBJ files or archives.
  2. Script Configuration:
      Adjust the maximum workers for processing STL files.
      Enable/disable specific scripts:
        Combine Script: Merges similar models into a unified structure.
        Delete Empty Folders: Deletes empty or irrelevant folders.
  3. Progress Monitoring: View the progress of the processing in the GUI.
  4. Logs: Real-time logs provide detailed feedback.

Script Workflow
  1. Archive Extraction: Automatically extracts .rar, .zip, and .7z files.
  2. File Combination: Combines related files into a single folder.
  3. Image Rendering: Generates PNG previews (top and front views) of 3D models.
  4. Folder Cleanup: Removes unnecessary or empty folders based on user-defined rules.

Acknowledgments
  Built using PyRender for 3D rendering.
  Inspired by the need for faster cataloging in 3D printing workflows.
