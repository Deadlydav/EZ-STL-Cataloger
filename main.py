import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import signal
import time

class ScriptGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EZ STL Cataloger")
        self.root.geometry("600x600")
        
        # Add window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Variables
        self.input_folder_path = tk.StringVar()
        self.stlphoto_max_workers = tk.StringVar(value="4")
        self.delete_empty_enabled = tk.BooleanVar(value=False)
        self.combine_enabled = tk.BooleanVar(value=True)
        self.delete_mode = tk.StringVar(value="all")
        self.min_images = tk.StringVar(value="3")
        
        # Queue for thread communication
        self.queue = queue.Queue()
        self.running = False
        self.current_process = None
        self.stop_requested = False
        
        self.create_widgets()

    def create_widgets(self):
        # Input Folder selection
        input_folder_frame = ttk.LabelFrame(self.root, text="Input Folder Selection", padding=10)
        input_folder_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Entry(input_folder_frame, textvariable=self.input_folder_path, width=50).pack(side="left", padx=5)
        ttk.Button(input_folder_frame, text="Browse", command=self.browse_input_folder).pack(side="left")

        # Script Configuration
        config_frame = ttk.LabelFrame(self.root, text="Script Configuration", padding=10)
        config_frame.pack(fill="x", padx=10, pady=5)

        # STL Photo options
        ttk.Label(config_frame, text="STL Photo Max Workers:").pack(anchor="w")
        ttk.Entry(config_frame, textvariable=self.stlphoto_max_workers, width=10).pack(fill="x", pady=2)

        # Add script toggles with descriptions
        combine_frame = ttk.Frame(config_frame)
        combine_frame.pack(fill="x", pady=5)
        
        combine_cb = ttk.Checkbutton(combine_frame, text="Enable Combine Script", 
                                   variable=self.combine_enabled)
        combine_cb.pack(side="left", padx=5)
        
        combine_info = ttk.Label(combine_frame, 
            text="ℹ️",
            cursor="hand2")
        combine_info.pack(side="left")
        
        # Create tooltip for combine script
        self.combine_tooltip = None
        combine_desc = (
            "Combine Script Description:\n"
            "------------------------\n"
            "This script combines multiple STL files from subfolders into a single folder.\n\n"
            "Use cases:\n"
            "• Merges similar models from numbered folders (e.g., model-001, model-002)\n"
            "• Consolidates files from extracted archives\n"
            "• Organizes scattered STL files into a unified structure\n\n"
            "Example:\n"
            "Before:\n"
            "  └── MainFolder\n"
            "      ├── Model-001\n"
            "      │   └── figure.stl\n"
            "      └── Model-002\n"
            "          └── figure.stl\n"
            "After:\n"
            "  └── MainFolder\n"
            "      ├── figure-001.stl\n"
            "      └── figure-002.stl"
        )
        
        def show_combine_tooltip(event):
            x, y, _, _ = combine_info.bbox("insert")
            x += combine_info.winfo_rootx() + 25
            y += combine_info.winfo_rooty() + 20
            
            # Destroy existing tooltip if it exists
            if self.combine_tooltip:
                self.combine_tooltip.destroy()
            
            # Create new tooltip
            self.combine_tooltip = tk.Toplevel(self.root)
            self.combine_tooltip.wm_overrideredirect(True)
            self.combine_tooltip.wm_geometry(f"+{x}+{y}")
            
            label = ttk.Label(self.combine_tooltip, text=combine_desc,
                            justify="left", background="#ffffe0", 
                            relief="solid", borderwidth=1,
                            padding=5)
            label.pack()
            
        def hide_combine_tooltip(event):
            if self.combine_tooltip:
                self.combine_tooltip.destroy()
                self.combine_tooltip = None
        
        combine_info.bind('<Enter>', show_combine_tooltip)
        combine_info.bind('<Leave>', hide_combine_tooltip)

        # Delete Empty Folders section
        delete_frame = ttk.LabelFrame(config_frame, text="Delete Empty Folders Options", padding=5)
        delete_frame.pack(fill="x", pady=5)

        # Main toggle
        ttk.Checkbutton(delete_frame, text="Enable Delete Empty Folders", 
                       variable=self.delete_empty_enabled).pack(anchor="w")

        # Mode selection
        mode_frame = ttk.Frame(delete_frame)
        mode_frame.pack(fill="x", pady=2)
        ttk.Label(mode_frame, text="Delete Mode:").pack(side="left", padx=5)
        modes = [
            ("All image folders", "all"),
            ("Folders with few images", "few"),
            ("Empty folders only", "keep")
        ]
        for text, mode in modes:
            ttk.Radiobutton(mode_frame, text=text, variable=self.delete_mode, 
                          value=mode).pack(side="left", padx=5)

        # Minimum images option
        min_frame = ttk.Frame(delete_frame)
        min_frame.pack(fill="x", pady=2)
        ttk.Label(min_frame, text="Minimum images to keep:").pack(side="left", padx=5)
        ttk.Entry(min_frame, textvariable=self.min_images, width=5).pack(side="left")

        # Progress Frame
        progress_frame = ttk.LabelFrame(self.root, text="Progress", padding=10)
        progress_frame.pack(fill="x", padx=10, pady=5)
        
        self.progress_var = tk.StringVar(value="")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.pack(anchor="w")
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill="x", pady=5)

        # Buttons Frame
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(pady=5)
        
        # Run button
        self.run_button = ttk.Button(buttons_frame, text="Run Scripts", command=self.start_scripts)
        self.run_button.pack(side="left", padx=5)

        # Stop button
        self.stop_button = ttk.Button(buttons_frame, text="Stop", command=self.stop_scripts, state="disabled")
        self.stop_button.pack(side="left", padx=5)

        # Emergency Stop button
        self.emergency_stop_button = ttk.Button(buttons_frame, text="Emergency Stop", 
                                              command=self.emergency_stop, 
                                              style="Emergency.TButton",
                                              state="disabled")
        self.emergency_stop_button.pack(side="left", padx=5)

        # Create emergency button style
        style = ttk.Style()
        style.configure("Emergency.TButton", foreground="red")

        # Log area
        log_frame = ttk.LabelFrame(self.root, text="Log", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, wrap="word")
        self.log_text.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=scrollbar.set)

        # Start checking the queue
        self.check_queue()

    def check_queue(self):
        try:
            while True:
                message = self.queue.get_nowait()
                if isinstance(message, tuple):
                    if message[0] == "log":
                        self.log_message(message[1])
                    elif message[0] == "progress":
                        current, total = message[1], message[2]
                        percentage = (current / total) * 100
                        self.progress_var.set(f"Processing: {current}/{total} ({percentage:.1f}%)")
                        self.progress_bar['value'] = percentage
                    elif message[0] == "done":
                        self.running = False
                        self.run_button.config(state="normal")
                        self.stop_button.config(state="disabled")
                        self.emergency_stop_button.config(state="disabled")
                        messagebox.showinfo("Success", "All scripts completed successfully!")
                    elif message[0] == "error":
                        self.running = False
                        self.run_button.config(state="normal")
                        self.stop_button.config(state="disabled")
                        self.emergency_stop_button.config(state="disabled")
                        messagebox.showerror("Error", message[1])
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.check_queue)

    def browse_input_folder(self):
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_folder_path.set(folder)

    def log_message(self, message):
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")

    def run_script(self, script_name, input_path):
        if self.stop_requested:
            return False

        self.queue.put(("log", f"\n=== Running {script_name} ==="))
        try:
            cmd = [sys.executable, script_name, input_path]
            
            if sys.platform == "win32":
                self.current_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                                      text=True, bufsize=1, universal_newlines=True)
            else:
                self.current_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                                      text=True, bufsize=1, universal_newlines=True, 
                                                      preexec_fn=os.setsid)

            while True:
                if self.stop_requested:
                    self.current_process.terminate()
                    self.queue.put(("log", f"Stopped {script_name}"))
                    return False

                output = self.current_process.stdout.readline()
                if output == '' and self.current_process.poll() is not None:
                    break
                if output:
                    self.queue.put(("log", output.strip()))

            return_code = self.current_process.wait()
            if return_code != 0:
                raise subprocess.CalledProcessError(return_code, cmd)

            if script_name == "scriptdeletempty.py":
                cmd.extend([self.min_images.get(), self.delete_mode.get()])

            return True

        except Exception as e:
            self.queue.put(("log", f"Error running {script_name}:"))
            self.queue.put(("log", str(e)))
            raise

    def run_scripts(self):
        input_path = self.input_folder_path.get()
        if not input_path:
            self.queue.put(("error", "Please select an input folder first!"))
            return
        
        if not os.path.isdir(input_path):
            self.queue.put(("error", f"Invalid input directory: {input_path}"))
            return

        try:
            # Run preprocessing scripts
            for script in ["scriptunzipmultirar.py", "script7zextract.py"]:
                if not self.run_script(script, input_path):
                    return

            # Run combine script only if enabled
            if self.combine_enabled.get():
                if not self.run_script("scriptcombine.py", input_path):
                    return

            # Launch stlphoto18.py in new terminal
            folder_path = self.input_folder_path.get()
            max_workers = self.stlphoto_max_workers.get()
            script_path = os.path.join(os.path.dirname(__file__), "stlphoto18.py")
            
            if sys.platform == "win32":
                # Wrap the path in quotes to handle spaces
                cmd = f'start cmd /k "python "{script_path}" "{folder_path}" {max_workers}"'
                subprocess.Popen(cmd, shell=True)
            else:
                terminal_cmd = 'gnome-terminal' if os.system('which gnome-terminal') == 0 else 'xterm'
                cmd = [terminal_cmd, '--', 'python3', script_path, folder_path, str(max_workers)]
                subprocess.Popen(cmd)

            # Run post-processing script only if enabled
            if self.delete_empty_enabled.get():
                if not self.run_script("scriptdeletempty.py", input_path):
                    return

            if not self.stop_requested:
                self.queue.put(("done", None))
                
        except Exception as e:
            self.queue.put(("error", f"An error occurred: {str(e)}"))
        finally:
            self.running = False
            self.stop_requested = False
            self.current_process = None
            self.run_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.emergency_stop_button.config(state="disabled")

    def start_scripts(self):
        if not self.running:
            self.running = True
            self.stop_requested = False
            self.run_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.emergency_stop_button.config(state="normal")
            threading.Thread(target=self.run_scripts, daemon=True).start()

    def stop_scripts(self):
        if self.running:
            self.stop_requested = True
            self.queue.put(("log", "\nStop requested. Waiting for current operation to complete..."))
            self.stop_button.config(state="disabled")

    def emergency_stop(self):
        if self.current_process:
            self.queue.put(("log", "\nEmergency stop triggered! Terminating process..."))
            try:
                if sys.platform == "win32":
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.current_process.pid)])
                else:
                    os.killpg(os.getpgid(self.current_process.pid), signal.SIGKILL)
            except Exception as e:
                print(f"Error during emergency stop: {e}")
            
            self.current_process = None
            self.running = False
            self.stop_requested = False
            self.run_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.emergency_stop_button.config(state="disabled")
            self.queue.put(("progress_msg", "Process terminated"))
            self.progress_bar['value'] = 0

    def on_closing(self):
        if self.running:
            if messagebox.askokcancel("Quit", "A process is still running. Do you want to terminate it and quit?"):
                if self.current_process:
                    self.emergency_stop()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    root = tk.Tk()
    app = ScriptGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
