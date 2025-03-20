import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import platform
from plotting import *
from processor import DataProcessor


class RheologyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Rheology Data Analyzer")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self.output_directory = self.get_output_directory()
        self.selected_viscosity_files = []
        self.selected_thixotropy_files = []
        self.processor = DataProcessor(self.output_directory)  # Create processor at initialization

        self.create_widgets()

    def get_output_directory(self):
        try:
            with open("config.txt", "r") as file:
                return file.readline().strip()
        except FileNotFoundError:
            return os.path.join(os.path.expanduser("~"), "Documents")

    def create_widgets(self):
        # Create frame for main content
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create viscosity tab
        viscosity_frame = ttk.Frame(notebook, padding="10")
        notebook.add(viscosity_frame, text="Viscosity")

        # Create thixotropy tab
        thixotropy_frame = ttk.Frame(notebook, padding="10")
        notebook.add(thixotropy_frame, text="Thixotropy")

        # Setup viscosity tab
        self.setup_viscosity_tab(viscosity_frame)

        # Setup thixotropy tab
        self.setup_thixotropy_tab(thixotropy_frame)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set(f"Output directory: {self.output_directory}")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_viscosity_tab(self, parent):
        # File selection frame
        file_frame = ttk.LabelFrame(parent, text="File Selection", padding="10")
        file_frame.pack(fill=tk.X, padx=5, pady=5)

        # Radio buttons for file mode
        self.viscosity_file_mode = tk.StringVar(value="S")
        ttk.Radiobutton(file_frame, text="Single File", variable=self.viscosity_file_mode, value="S").grid(row=0,
                                                                                                           column=0,
                                                                                                           sticky=tk.W)
        ttk.Radiobutton(file_frame, text="Multiple Files", variable=self.viscosity_file_mode, value="M").grid(row=0,
                                                                                                              column=1,
                                                                                                              sticky=tk.W)

        # File selection button
        ttk.Button(file_frame, text="Select File(s)", command=self.select_viscosity_files).grid(row=0, column=2, padx=5)

        # File list
        self.viscosity_file_list = tk.Listbox(file_frame, height=5, width=70)
        self.viscosity_file_list.grid(row=1, column=0, columnspan=3, sticky=tk.EW, pady=5)

        # Scrollbar for file list
        scrollbar = ttk.Scrollbar(file_frame, orient=tk.VERTICAL, command=self.viscosity_file_list.yview)
        scrollbar.grid(row=1, column=3, sticky=tk.NS)
        self.viscosity_file_list.config(yscrollcommand=scrollbar.set)

        # Options frame
        options_frame = ttk.LabelFrame(parent, text="Plot Options", padding="10")
        options_frame.pack(fill=tk.X, padx=5, pady=5)

        # Sweep type
        ttk.Label(options_frame, text="Sweep Type:").grid(row=0, column=0, sticky=tk.W)
        self.sweep_type = tk.StringVar(value="FORWARD")
        ttk.Radiobutton(options_frame, text="Forward", variable=self.sweep_type, value="FORWARD").grid(row=0, column=1,
                                                                                                       sticky=tk.W)
        ttk.Radiobutton(options_frame, text="Reverse", variable=self.sweep_type, value="REVERSE").grid(row=0, column=2,
                                                                                                       sticky=tk.W)
        ttk.Radiobutton(options_frame, text="Both", variable=self.sweep_type, value="BOTH").grid(row=0, column=3,
                                                                                                 sticky=tk.W)

        # Plot type
        ttk.Label(options_frame, text="Plot Type:").grid(row=1, column=0, sticky=tk.W)
        self.plot_type = tk.StringVar(value="N")
        ttk.Radiobutton(options_frame, text="Normal", variable=self.plot_type, value="N").grid(row=1, column=1,
                                                                                               sticky=tk.W)
        ttk.Radiobutton(options_frame, text="Derivative", variable=self.plot_type, value="D").grid(row=1, column=2,
                                                                                                   sticky=tk.W)

        # Action buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=10)

        ttk.Button(button_frame, text="Process and Plot", command=self.process_viscosity).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Clear Selection", command=self.clear_viscosity_selection).pack(side=tk.RIGHT,
                                                                                                      padx=5)

    def setup_thixotropy_tab(self, parent):
        # File selection frame
        file_frame = ttk.LabelFrame(parent, text="File Selection", padding="10")
        file_frame.pack(fill=tk.X, padx=5, pady=5)

        # Radio buttons for file mode
        self.thixotropy_file_mode = tk.StringVar(value="S")
        ttk.Radiobutton(file_frame, text="Single File", variable=self.thixotropy_file_mode, value="S").grid(row=0,
                                                                                                            column=0,
                                                                                                            sticky=tk.W)
        ttk.Radiobutton(file_frame, text="Multiple Files", variable=self.thixotropy_file_mode, value="M").grid(row=0,
                                                                                                               column=1,
                                                                                                               sticky=tk.W)

        # File selection button
        ttk.Button(file_frame, text="Select File(s)", command=self.select_thixotropy_files).grid(row=0, column=2,
                                                                                                 padx=5)

        # File list
        self.thixotropy_file_list = tk.Listbox(file_frame, height=5, width=70)
        self.thixotropy_file_list.grid(row=1, column=0, columnspan=3, sticky=tk.EW, pady=5)

        # Scrollbar for file list
        scrollbar = ttk.Scrollbar(file_frame, orient=tk.VERTICAL, command=self.thixotropy_file_list.yview)
        scrollbar.grid(row=1, column=3, sticky=tk.NS)
        self.thixotropy_file_list.config(yscrollcommand=scrollbar.set)

        # Action buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=10)

        ttk.Button(button_frame, text="Process and Plot", command=self.process_thixotropy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Clear Selection", command=self.clear_thixotropy_selection).pack(side=tk.RIGHT,
                                                                                                       padx=5)

    def select_viscosity_files(self):
        multiple = self.viscosity_file_mode.get() == "M"
        if multiple:
            file_paths = filedialog.askopenfilenames(
                title="Select Viscosity Data Files",
                filetypes=[("Excel Files", "*.xls")]
            )
            self.selected_viscosity_files = file_paths
        else:
            file_path = filedialog.askopenfilename(
                title="Select Viscosity Data File",
                filetypes=[("Excel Files", "*.xls")]
            )
            self.selected_viscosity_files = [file_path] if file_path else []

        self.update_viscosity_file_list()

    def select_thixotropy_files(self):
        multiple = self.thixotropy_file_mode.get() == "M"
        if multiple:
            file_paths = filedialog.askopenfilenames(
                title="Select Thixotropy Data Files",
                filetypes=[("Excel Files", "*.xls")]
            )
            self.selected_thixotropy_files = file_paths
        else:
            file_path = filedialog.askopenfilename(
                title="Select Thixotropy Data File",
                filetypes=[("Excel Files", "*.xls")]
            )
            self.selected_thixotropy_files = [file_path] if file_path else []

        self.update_thixotropy_file_list()

    def update_viscosity_file_list(self):
        self.viscosity_file_list.delete(0, tk.END)
        for file_path in self.selected_viscosity_files:
            self.viscosity_file_list.insert(tk.END, os.path.basename(file_path))

    def update_thixotropy_file_list(self):
        self.thixotropy_file_list.delete(0, tk.END)
        for file_path in self.selected_thixotropy_files:
            self.thixotropy_file_list.insert(tk.END, os.path.basename(file_path))

    def clear_viscosity_selection(self):
        self.selected_viscosity_files = []
        self.update_viscosity_file_list()

    def clear_thixotropy_selection(self):
        self.selected_thixotropy_files = []
        self.update_thixotropy_file_list()

    def process_viscosity(self):
        if not hasattr(self, 'selected_viscosity_files') or not self.selected_viscosity_files:
            messagebox.showwarning("No Files Selected", "Please select at least one file to process.")
            return

        mode = self.viscosity_file_mode.get()
        plot_type = self.plot_type.get()
        sweep_type_value = self.sweep_type.get()

        # Convert sweep type for processor
        if sweep_type_value == "BOTH":
            sweep_type = ["FORWARD", "REVERSE"]
        else:
            sweep_type = sweep_type_value

        try:
            if mode == "S":
                file_path = self.selected_viscosity_files[0]

                if plot_type == "N":
                    df, fig_name, full_output_path = self.processor.process_viscosity_single(file_path, sweep_type)
                else:  # plot_type == "D"
                    df, fig_name, full_output_path = self.processor.process_diff_viscosity_single(file_path, sweep_type)

                self.status_var.set(f"Plot saved: {os.path.basename(full_output_path)}")
            else:  # mode == "M"
                dataframes, dataset_names, fig_name, full_output_path = self.processor.process_viscosity_multiple(
                    self.selected_viscosity_files, sweep_type
                )
                self.status_var.set(f"Comparison plot saved: {os.path.basename(full_output_path)}")

            if os.path.exists(full_output_path):
                open_result = messagebox.askyesno("Success",
                                                  f"Plot saved successfully to:\n{full_output_path}\n\nWould you like to open the plot?")
                if open_result:
                    # Open the plot file with the default application
                    os.startfile(full_output_path)
            else:
                messagebox.showwarning("Warning", "Plot file not found at expected location")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during processing: {str(e)}")

    def process_thixotropy(self):
        if not hasattr(self, 'selected_thixotropy_files') or not self.selected_thixotropy_files:
            messagebox.showwarning("No Files Selected", "Please select at least one file to process.")
            return

        mode = self.thixotropy_file_mode.get()

        try:
            if mode == "S":
                file_path = self.selected_thixotropy_files[0]
                df, fig_name, full_output_path = self.processor.process_thixotropy_single(file_path)
                self.status_var.set(f"Plot saved: {os.path.basename(full_output_path)}")
            else:  # mode == "M"
                dataframes, dataset_names, fig_name, full_output_path = self.processor.process_thixotropy_multiple(
                    self.selected_thixotropy_files
                )
                self.status_var.set(f"Comparison plot saved: {os.path.basename(full_output_path)}")

            if os.path.exists(full_output_path):
                open_result = messagebox.askyesno("Success",
                                                  f"Plot saved successfully to:\n{full_output_path}\n\nWould you like to open the plot?")
                if open_result:
                    # Open the plot file with the default application
                    os.startfile(full_output_path)
            else:
                messagebox.showwarning("Warning", "Plot file not found at expected location")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during processing: {str(e)}")


def main():
    root = tk.Tk()
    app = RheologyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()