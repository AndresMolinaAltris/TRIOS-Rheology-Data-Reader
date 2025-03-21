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

        # Results frame
        results_frame = ttk.LabelFrame(parent, text="Analysis Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create a Treeview widget to display results in a table
        columns = ("Metric", "Value")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=5)

        # Configure columns
        self.results_tree.heading("Metric", text="Metric")
        self.results_tree.heading("Value", text="Value")
        self.results_tree.column("Metric", width=250)
        self.results_tree.column("Value", width=150)

        # Add scrollbar
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)

        # Grid layout for results tree and scrollbar
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Export options frame
        export_frame = ttk.LabelFrame(parent, text="Export Options", padding="10")
        export_frame.pack(fill=tk.X, padx=5, pady=5)

        # Export format
        ttk.Label(export_frame, text="Export Format:").grid(row=0, column=0, sticky=tk.W)
        self.export_format = tk.StringVar(value="csv")
        ttk.Radiobutton(export_frame, text="CSV", variable=self.export_format, value="csv").grid(
            row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(export_frame, text="Excel", variable=self.export_format, value="excel").grid(
            row=0, column=2, sticky=tk.W)

        # Export button
        ttk.Button(export_frame, text="Export Results", command=self.export_thixotropy_results).grid(
            row=0, column=3, padx=5)

        # Action buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=10)

        # New analyze button
        ttk.Button(
            button_frame,
            text="Analyze Thixotropy",
            command=self.analyze_thixotropy
        ).pack(side=tk.RIGHT, padx=5)

        # Regular plot button
        ttk.Button(
            button_frame,
            text="Process and Plot",
            command=self.process_thixotropy
        ).pack(side=tk.RIGHT, padx=5)

        # Clear button
        ttk.Button(
            button_frame,
            text="Clear Selection",
            command=self.clear_thixotropy_selection
        ).pack(side=tk.RIGHT, padx=5)

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
        # Clear the results tree as well
        self.clear_results_display()

        # Reset stored results
        self.current_results = None
        self.current_multiple_results = None

    def clear_results_display(self):
        """Clear all items from the results treeview."""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

    def display_thixotropy_results(self, results):
        """
        Display thixotropy analysis results in the treeview.

        Parameters:
        results (dict): Dictionary containing metric names and values
        """
        # Store the results for potential export
        self.current_results = results
        self.current_multiple_results = None

        # Clear existing data
        self.clear_results_display()

        # Add new results to the treeview
        for metric, value in results.items():
            # Format numerical values to 2 decimal places if applicable
            if isinstance(value, (int, float)):
                formatted_value = f"{value:.2f}" if isinstance(value, float) else str(value)
            else:
                formatted_value = str(value)

            self.results_tree.insert("", tk.END, values=(metric, formatted_value))

        # Update status
        self.status_var.set("Thixotropy analysis completed")

    def display_multiple_thixotropy_results(self, all_results):
        """
        Display results from multiple files in the treeview.

        Parameters:
        all_results (dict): Dictionary mapping sample names to result dictionaries
        """
        # Store the results for potential export
        self.current_results = None
        self.current_multiple_results = all_results

        # Clear existing data
        self.clear_results_display()

        # For multiple samples, we'll organize by sample name first
        for sample_name, results in all_results.items():
            # Add the sample name as a parent item
            sample_id = self.results_tree.insert("", tk.END, text=sample_name,
                                                 values=(sample_name, ""))

            # Add the sample's metrics as child items
            for metric, value in results.items():
                if isinstance(value, (int, float)):
                    formatted_value = f"{value:.2f}" if isinstance(value, float) else str(value)
                else:
                    formatted_value = str(value)

                self.results_tree.insert(sample_id, tk.END, values=(metric, formatted_value))

        # Update status
        self.status_var.set(f"Analyzed {len(all_results)} samples")

    def analyze_thixotropy(self):
        """
        Analyze thixotropy data and display results without creating plots.
        """
        if not hasattr(self, 'selected_thixotropy_files') or not self.selected_thixotropy_files:
            messagebox.showwarning("No Files Selected", "Please select at least one file to analyze.")
            return

        mode = self.thixotropy_file_mode.get()

        try:
            if mode == "S":
                # Single file analysis
                file_path = self.selected_thixotropy_files[0]
                _, results = self.processor.analyze_thixotropy_single(file_path)

                if "Error" in results:
                    messagebox.showerror("Analysis Error", results["Error"])
                else:
                    self.display_thixotropy_results(results)
                    messagebox.showinfo("Analysis Complete",
                                        "Thixotropy analysis completed successfully.")

            else:  # Multiple files
                # Multiple file analysis
                all_results = self.processor.analyze_thixotropy_multiple(self.selected_thixotropy_files)

                # Check if any files had errors
                errors = [f"{sample}: {results['Error']}"
                          for sample, results in all_results.items()
                          if "Error" in results]

                if errors:
                    error_message = "Errors occurred during analysis:\n" + "\n".join(errors)
                    messagebox.showwarning("Analysis Warning", error_message)

                # Display all results, including any that were successful
                self.display_multiple_thixotropy_results(all_results)

                # Show success message if at least some files were analyzed successfully
                successful = len(all_results) - len(errors)
                if successful > 0:
                    messagebox.showinfo("Analysis Complete",
                                        f"Successfully analyzed {successful} out of {len(all_results)} files.")

        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An error occurred during analysis: {str(e)}")
            # Log the full error for debugging
            print(f"Error in analyze_thixotropy: {e}")

    def export_thixotropy_results(self):
        """
        Export the current thixotropy analysis results to a file.
        """
        # Check if we have results to export
        if self.current_results is None and self.current_multiple_results is None:
            messagebox.showwarning("No Results", "Please analyze data before exporting results.")
            return

        # Get export format
        export_format = self.export_format.get()
        file_extension = ".csv" if export_format == "csv" else ".xlsx"

        # Ask user for save location
        file_types = [("CSV Files", "*.csv")] if export_format == "csv" else [("Excel Files", "*.xlsx")]
        default_filename = "thixotropy_results" + file_extension

        save_path = filedialog.asksaveasfilename(
            title="Save Results As",
            filetypes=file_types,
            defaultextension=file_extension,
            initialfile=default_filename,
            initialdir=self.output_directory
        )

        if not save_path:
            return  # User cancelled

        try:
            # Export based on what type of results we have
            if self.current_results is not None:
                # Single file results
                success, message = self.processor.export_thixotropy_results_single(
                    self.current_results, save_path, export_format)
            else:
                # Multiple file results
                success, message = self.processor.export_thixotropy_results_multiple(
                    self.current_multiple_results, save_path, export_format)

            # Show appropriate message
            if success:
                messagebox.showinfo("Export Successful",
                                    f"Results exported successfully to:\n{message}")

                # Ask if user wants to open the file
                open_file = messagebox.askyesno("Open File",
                                                "Would you like to open the exported file?")
                if open_file:
                    self.open_file(save_path)
            else:
                messagebox.showerror("Export Failed", message)

        except Exception as e:
            messagebox.showerror("Export Error", f"An unexpected error occurred during export: {str(e)}")

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
                self.open_file(full_output_path)
        else:
            messagebox.showwarning("Warning", "Plot file not found at expected location")

    def process_thixotropy(self):
        if not hasattr(self, 'selected_thixotropy_files') or not self.selected_thixotropy_files:
            messagebox.showwarning("No Files Selected", "Please select at least one file to process.")
            return

        mode = self.thixotropy_file_mode.get()

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
                self.open_file(full_output_path)
        else:
            messagebox.showwarning("Warning", "Plot file not found at expected location")

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


def main():
    root = tk.Tk()
    app = RheologyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()