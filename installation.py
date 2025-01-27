import subprocess
import sys
import os
import pkg_resources
import platform

def print_status(message):
    print(f"\n=== {message} ===")

def check_python_version():
    print_status("Checking Python Version")
    python_version = sys.version_info
    min_version = (3, 8)
    recommended_version = (3, 11)
    
    print(f"Current Python version: {python_version.major}.{python_version.minor}")
    
    if python_version < min_version:
        print(f"Error: Python version {min_version[0]}.{min_version[1]} or higher is required")
        return False
    elif python_version > recommended_version:
        print(f"Warning: Python version {python_version.major}.{python_version.minor} is newer than recommended version {recommended_version[0]}.{recommended_version[1]}")
        print("Some packages might not be fully compatible")
    else:
        print("Python version check passed")
    return True

def install_package(package_name, version=None):
    try:
        if version:
            package_spec = f"{package_name}=={version}"
        else:
            package_spec = package_name
            
        print(f"Installing {package_spec}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_spec])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing {package_name}: {e}")
        return False

def check_and_install_packages():
    print_status("Installing/Updating Required Packages")
    
    # List of required packages with their minimum versions
    required_packages = {
        'numpy': '1.20.0',
        'trimesh': '3.9.0',
        'pyrender': '0.1.45',
        'Pillow': '8.0.0',
        'py7zr': '0.20.0',
        'rarfile': '4.0',
        'scipy': '1.7.0',
        'pyglet': '1.5.0',
        'networkx': '2.5'
    }
    
    success = True
    for package, version in required_packages.items():
        try:
            pkg_resources.require(f"{package}>={version}")
            print(f"{package} is already installed with correct version")
        except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
            if not install_package(package, version):
                success = False
    
    return success

def check_system_dependencies():
    print_status("Checking System Dependencies")
    system = platform.system()
    
    if system == "Windows":
        # Check for WinRAR
        winrar_path = r"C:\Program Files\WinRAR\WinRAR.exe"
        if not os.path.exists(winrar_path):
            print("Warning: WinRAR not found in default location")
            print("Please install WinRAR from: https://www.win-rar.com/")
    
    elif system == "Linux":
        # Check for unrar
        try:
            subprocess.check_call(["which", "unrar"], stdout=subprocess.DEVNULL)
            print("unrar is installed")
        except subprocess.CalledProcessError:
            print("Warning: unrar is not installed")
            print("Please install it using your package manager:")
            print("Ubuntu/Debian: sudo apt-get install unrar")
            print("Fedora: sudo dnf install unrar")
        
        # Check for OpenGL dependencies
        try:
            import OpenGL
            print("OpenGL is installed")
        except ImportError:
            print("Warning: OpenGL is not installed")
            print("Please install required packages:")
            print("Ubuntu/Debian: sudo apt-get install python3-opengl")
            print("Ubuntu/Debian: sudo apt-get install libgles2-mesa-dev")

def create_test_file():
    print_status("Creating Test Files")
    
    test_scripts = {
        "test_numpy.py": """
import numpy as np
print("NumPy test successful")
""",
        "test_trimesh.py": """
import trimesh
print("Trimesh test successful")
""",
        "test_pyrender.py": """
import pyrender
print("Pyrender test successful")
""",
        "test_pillow.py": """
from PIL import Image
print("Pillow test successful")
"""
    }
    
    for filename, content in test_scripts.items():
        with open(filename, 'w') as f:
            f.write(content.strip())
        try:
            subprocess.check_call([sys.executable, filename])
            os.remove(filename)
            print(f"✓ {filename} passed")
        except subprocess.CalledProcessError:
            print(f"✗ {filename} failed")

def main():
    print("Starting installation and dependency check...")
    
    if not check_python_version():
        sys.exit(1)
    
    try:
        # Upgrade pip first
        print_status("Upgrading pip")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        if not check_and_install_packages():
            print("\nSome packages failed to install. Please check the errors above.")
            sys.exit(1)
        
        check_system_dependencies()
        create_test_file()
        
        print("\n=== Installation Complete ===")
        print("All required packages have been installed and tested.")
        print("\nIf you encountered any warnings above, please address them before running the scripts.")
        
    except Exception as e:
        print(f"\nAn error occurred during installation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 