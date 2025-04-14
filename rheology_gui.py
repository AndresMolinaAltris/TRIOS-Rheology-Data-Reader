import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import platform
import os
from plotting import *
from processor import DataProcessor
from file_selector import FileSelector  # Changed to match your file name


class RheologyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Rheology Data Analyzer")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)

        self.output_directory = self.get_output_directory()
        self.selected_viscosity_files = []
        self.selected_thixotropy_files = []
        self.processor = DataProcessor(self.output_directory)

        # Store analysis results for potential export
        self.current_results = None
        self.current_multiple_results = None

        self.create_widgets()

    def get_output_directory(self):
        try:
            with open("config.txt", "r") as file:
                return file.readline().strip()
        except FileNotFoundError:
            return os.path.join(os.path.expanduser("~"), "Documents")

    def create_widgets(self):
        # Configure the root window grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Create viscosity tab using our file selector component
        self.viscosity_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.viscosity_tab, text="Viscosity")

        # Create the file selector within the tab
        self.viscosity_file_selector = FileSelector(self.viscosity_tab,
                                                    initial_dir=self.output_directory)
        self.viscosity_file_selector.pack(fill=tk.BOTH, expand=True)

        # Create the second tab (empty for now)
        self.future_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.future_tab, text="Future Implementation")

        # Add a simple label to the second tab
        ttk.Label(self.future_tab,
                  text="This tab is reserved for future implementation.",
                  font=("Arial", 12)).pack(expand=True)

        # Status bar at the bottom of the main window
        self.status_var = tk.StringVar()
        self.status_var.set(f"Output directory: {self.output_directory}")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=1, column=0, sticky="ew")

    def open_file(self, file_path):
        """Open a file with the default application."""
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', file_path], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', file_path], check=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")