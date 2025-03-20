import tkinter as tk
from tkinter import filedialog
from plotting import *


# UI Logic - Handles user interaction
class UserInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main Tkinter window

    def get_experiment_type(self):
        """Prompt user to select experiment type."""
        while True:
            experiment = input("Viscosity (V) or Thixotropy (T)? ").strip().upper()
            if experiment in ['V', 'T']:
                return experiment
            print("Invalid input. Please enter 'V' or 'T'.")

    def get_file_mode(self):
        """Prompt user to select single or multiple file mode."""
        while True:
            mode = input("Select single file (S) or multiple files (M)? ").strip().upper()
            if mode in ['S', 'M']:
                return mode
            print("Invalid input. Please enter 'S' or 'M'.")

    def get_sweep_type(self):
        """Prompt user to select sweep type."""
        while True:
            sweep_input = input("Plot FORWARD (F), REVERSE (R), or BOTH (B) sweeps? ").strip().upper()
            if sweep_input == 'F':
                return "FORWARD"
            elif sweep_input == 'R':
                return "REVERSE"
            elif sweep_input == 'B':
                return ["FORWARD", "REVERSE"]
            else:
                print("Invalid input. Please enter 'F', 'R', or 'B'.")

    def select_files(self, multiple=False):
        """Opens a file dialog to select one or multiple data files."""
        if multiple:
            file_paths = filedialog.askopenfilenames(
                title="Select Data Files",
                filetypes=[("Excel Files", "*.xls")]
            )
            return file_paths if file_paths else []
        else:
            file_path = filedialog.askopenfilename(
                title="Select Data File",
                filetypes=[("Excel Files", "*.xls")]
            )
            return file_path

    def display_selected_files(self, file_paths):
        """Display information about selected files."""
        if isinstance(file_paths, list):
            print(f"Selected {len(file_paths)} files:")
            for path in file_paths:
                print(f"  - {path}")
        else:
            print(f"Selected file: {file_paths}")

    def display_data_loaded(self, df):
        """Display information about loaded data."""
        if isinstance(df, list):
            print(f"Loaded {len(df)} datasets.")
        else:
            print(f"Data loaded successfully. Shape: {df.shape}")

    def display_plot_generation(self, fig_name):
        """Display information about plot generation."""
        print(f"Generating plot: {fig_name}")

    def display_save_status(self, full_output_path):
        """Display whether the plot was saved successfully."""
        if os.path.exists(full_output_path):
            print(f"Plot saved successfully: {full_output_path}")
        else:
            print(f"Warning: Plot file not found at expected location: {full_output_path}")

    def display_message(self, message):
        """Display a message to the user."""
        print(message)