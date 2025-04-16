import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import platform
import os

# Matplotlib imports
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Your other imports
from plotting import *
from processor import DataProcessor


class RheologyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Rheology Data Analyzer")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)

        self.output_directory = self.get_output_directory()
        self.processor = DataProcessor(self.output_directory)

        # Initialize variables that will be used across methods
        self.selected_files = []
        self.viscosity_status_var = tk.StringVar(value="No files selected")

        # Create the UI
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

        # Create viscosity tab
        self.viscosity_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.viscosity_tab, text="Viscosity")

        # Set up the viscosity tab with file selector and plot areas
        self._setup_viscosity_tab()

        # Add the derivative tab
        self.derivative_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.derivative_tab, text="Viscosity Derivative")

        # Set up the derivative tab
        self._setup_derivative_tab()

        # Status bar at the bottom of the main window
        self.status_var = tk.StringVar()
        self.status_var.set(f"Output directory: {self.output_directory}")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=1, column=0, sticky="ew")

    def _setup_viscosity_tab(self):
        """Set up the viscosity tab with file selection and plot areas."""
        # Configure the viscosity tab layout
        self.viscosity_tab.columnconfigure(0, weight=1)
        self.viscosity_tab.rowconfigure(0, weight=0)  # File selection
        self.viscosity_tab.rowconfigure(1, weight=1)  # Plot area
        self.viscosity_tab.rowconfigure(2, weight=0)  # Control buttons

        # Create file selection area
        file_frame = ttk.Frame(self.viscosity_tab)
        file_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        # Setup file selection with the same structure as the file selector
        self._setup_file_selection(file_frame)

        # Create plot area
        plot_frame = ttk.LabelFrame(self.viscosity_tab, text="Plot Preview")
        plot_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        # Setup three plot areas
        self._setup_plot_area(plot_frame)

        # Create control buttons
        button_frame = ttk.Frame(self.viscosity_tab)
        button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        # Setup control buttons
        self._setup_control_buttons(button_frame)

    def _setup_file_selection(self, parent):
        """Create the file selection area with directory browsing."""
        # Directory selection
        dir_frame = ttk.Frame(parent)
        dir_frame.pack(fill=tk.X, pady=5)

        self.current_dir = tk.StringVar(value=self.output_directory)

        ttk.Label(dir_frame, text="Directory:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(dir_frame, textvariable=self.current_dir, width=60).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(dir_frame, text="Browse...", command=self._browse_directory).pack(side=tk.LEFT)

        # File selection area
        file_list_frame = ttk.Frame(parent)
        file_list_frame.pack(fill=tk.X, pady=5)

        file_list_frame.columnconfigure(0, weight=1)
        file_list_frame.columnconfigure(1, weight=0)
        file_list_frame.columnconfigure(2, weight=1)

        # Available files list
        avail_frame = ttk.LabelFrame(file_list_frame, text="Available XLS Files")
        avail_frame.grid(row=0, column=0, sticky="ew")

        avail_scrollbar = ttk.Scrollbar(avail_frame)
        avail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.available_listbox = tk.Listbox(avail_frame, height=5,
                                            selectmode=tk.EXTENDED,
                                            yscrollcommand=avail_scrollbar.set)
        self.available_listbox.pack(fill=tk.BOTH, expand=True)
        avail_scrollbar.config(command=self.available_listbox.yview)

        # Buttons
        button_frame = ttk.Frame(file_list_frame)
        button_frame.grid(row=0, column=1, padx=5)

        ttk.Button(button_frame, text=">>", command=self._add_selected_files).pack(pady=5)
        ttk.Button(button_frame, text="<<", command=self._remove_selected_files).pack(pady=5)

        # Selected files list
        selected_frame = ttk.LabelFrame(file_list_frame, text="Selected Files")
        selected_frame.grid(row=0, column=2, sticky="ew")

        selected_scrollbar = ttk.Scrollbar(selected_frame)
        selected_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.selected_listbox = tk.Listbox(selected_frame, height=5,
                                           selectmode=tk.EXTENDED,
                                           yscrollcommand=selected_scrollbar.set)
        self.selected_listbox.pack(fill=tk.BOTH, expand=True)
        selected_scrollbar.config(command=self.selected_listbox.yview)

        # Populate available files
        self._update_file_list()

        # Initialize selected files list
        self.selected_files = []

    def _setup_plot_area(self, parent):
        """Create the plot area with two plots (Forward and Reverse)."""
        # Create a frame with two columns for plots
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)

        # Create the plot containers and matplotlib figures
        self.plot_frames = []
        self.figures = []
        self.canvases = []

        titles = ["Forward Sweep", "Reverse Sweep"]  # Removed "Both Sweeps"

        for i in range(2):  # Changed from range(3) to range(2)
            frame = ttk.Frame(parent)
            frame.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)
            self.plot_frames.append(frame)

            # Create figure and canvas
            fig = Figure(figsize=(4, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.set_title(titles[i])
            ax.set_xlabel("Shear rate (1/s)")
            ax.set_ylabel("Viscosity (Pa.s)")
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.grid(True)
            self.figures.append(fig)

            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.canvases.append(canvas)

            # Add save button
            save_btn = ttk.Button(frame, text="Save Plot",
                                  command=lambda idx=i: self._save_plot(idx))
            save_btn.pack(side=tk.BOTTOM, pady=5)

    def _setup_control_buttons(self, parent):
        """Create the control buttons."""
        # Status display - define the variable FIRST before using it
        self.viscosity_status_var = tk.StringVar(value="No files selected")
        ttk.Label(parent, textvariable=self.viscosity_status_var).pack(side=tk.LEFT, padx=5)

        # Control buttons
        ttk.Button(parent, text="Exit",
                   command=self.root.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(parent, text="Process and Plot",
                   command=self._process_viscosity_files).pack(side=tk.RIGHT, padx=5)
        ttk.Button(parent, text="Clear Selection",
                   command=self._clear_viscosity_selection).pack(side=tk.RIGHT, padx=5)

    def _browse_directory(self):
        """Open directory browser dialog."""
        dir_path = filedialog.askdirectory(initialdir=self.current_dir.get())
        if dir_path:
            self.current_dir.set(dir_path)
            self._update_file_list()

    def _update_file_list(self):
        """Update available files listbox based on current directory."""
        self.available_listbox.delete(0, tk.END)
        try:
            # Get all XLS files in the directory
            xls_files = [f for f in os.listdir(self.current_dir.get())
                         if f.lower().endswith('.xls')]

            # Sort them alphabetically
            xls_files.sort()

            # Add to listbox
            for file in xls_files:
                self.available_listbox.insert(tk.END, file)

        except Exception as e:
            messagebox.showerror("Error", f"Error listing directory: {e}")

    def _add_selected_files(self):
        """Add files from available list to selected list."""
        selected_indices = self.available_listbox.curselection()
        for i in selected_indices:
            file_name = self.available_listbox.get(i)
            full_path = os.path.join(self.current_dir.get(), file_name)

            # Add if not already in list
            if full_path not in self.selected_files:
                self.selected_files.append(full_path)
                self.selected_listbox.insert(tk.END, file_name)

        # Update status
        self._update_viscosity_status()

    def _remove_selected_files(self):
        """Remove files from selected list."""
        selected_indices = self.selected_listbox.curselection()
        # Process in reverse to avoid index shifting
        for i in sorted(selected_indices, reverse=True):
            file_name = self.selected_listbox.get(i)
            # Find the full path in the selected_files list
            full_path = next((f for f in self.selected_files
                              if os.path.basename(f) == file_name), None)

            if full_path in self.selected_files:
                self.selected_files.remove(full_path)
            self.selected_listbox.delete(i)

        # Update status
        self._update_viscosity_status()

    def _clear_viscosity_selection(self):
        """Clear all selected files."""
        self.selected_files = []
        self.selected_listbox.delete(0, tk.END)
        self._update_viscosity_status()

    def _update_viscosity_status(self):
        """Update status display based on selected files."""
        count = len(self.selected_files)
        if count == 0:
            self.viscosity_status_var.set("No files selected")
        elif count == 1:
            self.viscosity_status_var.set("1 file selected")
        else:
            self.viscosity_status_var.set(f"{count} files selected")

    def _process_viscosity_files(self):
        """Process selected viscosity files and update plots."""
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select at least one file to process.")
            return

        try:
            # Update status
            self.viscosity_status_var.set(f"Processing {len(self.selected_files)} files...")
            self.root.update()

            # Process files for forward and reverse plots
            self._update_forward_plot(self.selected_files)
            self._update_reverse_plot(self.selected_files)

            # Now update the derivative plots
            self._update_forward_derivative(self.selected_files)
            self._update_reverse_derivative(self.selected_files)

            # Update status
            self.viscosity_status_var.set(f"Processed {len(self.selected_files)} files")
            self.derivative_status_var.set(f"Processed {len(self.selected_files)} files")

        except Exception as e:
            messagebox.showerror("Processing Error", f"Error processing files: {e}")
            self.viscosity_status_var.set("Error processing files")
            self.derivative_status_var.set("Error processing derivatives")

    def _update_forward_plot(self, file_paths):
        """Update the forward sweep plot."""
        if not isinstance(file_paths, list):
            file_paths = [file_paths]

        # Clear the plot
        ax = self.figures[0].axes[0]
        ax.clear()

        # Set plot properties
        ax.set_title("Forward Sweep")
        ax.set_xlabel("Shear rate (1/s)")
        ax.set_ylabel("Viscosity (Pa.s)")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.grid(True)

        # Process data and plot
        try:
            if len(file_paths) == 1:
                df, _, _ = self.processor.process_viscosity_single(file_paths[0], "FORWARD")
                forward_data = df[df["Sweep"] == "FORWARD"]

                # Plot the data
                label = os.path.basename(file_paths[0]).split('_')[0]
                ax.scatter(forward_data["Shear rate"], forward_data["Viscosity"],
                           label=label, color='blue')
            else:
                # Multiple files
                for i, file_path in enumerate(file_paths):
                    df, _, _ = self.processor.process_viscosity_single(file_path, "FORWARD")
                    forward_data = df[df["Sweep"] == "FORWARD"]

                    color = plt.cm.tab10(i % 10)

                    label = os.path.basename(file_path).split('_')[0]
                    ax.scatter(forward_data["Shear rate"], forward_data["Viscosity"],
                               label=label, color=color)

            ax.legend()
            self.canvases[0].draw()

        except Exception as e:
            print(f"Error updating forward plot: {e}")

    def _update_reverse_plot(self, file_paths):
        """Update the reverse sweep plot."""
        if not isinstance(file_paths, list):
            file_paths = [file_paths]

        # Clear the plot
        ax = self.figures[1].axes[0]
        ax.clear()

        # Set plot properties
        ax.set_title("Reverse Sweep")
        ax.set_xlabel("Shear rate (1/s)")
        ax.set_ylabel("Viscosity (Pa.s)")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.grid(True)

        # Process data and plot
        try:
            if len(file_paths) == 1:
                df, _, _ = self.processor.process_viscosity_single(file_paths[0], "REVERSE")
                reverse_data = df[df["Sweep"] == "REVERSE"]

                # Plot the data
                label = os.path.basename(file_paths[0]).split('_')[0]
                ax.scatter(reverse_data["Shear rate"], reverse_data["Viscosity"],
                           label=label, color='red')
            else:
                # Multiple files
                for i, file_path in enumerate(file_paths):
                    df, _, _ = self.processor.process_viscosity_single(file_path, "REVERSE")
                    reverse_data = df[df["Sweep"] == "REVERSE"]

                    color = plt.cm.tab10(i % 10)
                    label = os.path.basename(file_path).split('_')[0]
                    ax.scatter(reverse_data["Shear rate"], reverse_data["Viscosity"],
                               label=label, color=color)

            ax.legend()
            self.canvases[1].draw()

        except Exception as e:
            print(f"Error updating reverse plot: {e}")

    def _save_plot(self, plot_index):
        """Save the specified plot to a file."""
        plot_types = ["forward", "reverse"]  # Removed "both"

        # Create default filename
        default_name = f"viscosity_{plot_types[plot_index]}.png"

        # Ask user where to save the file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=default_name,
            initialdir=self.output_directory
        )

        if file_path:
            try:
                # Save the figure
                self.figures[plot_index].savefig(file_path, dpi=300, bbox_inches='tight')
                self.viscosity_status_var.set(f"Plot saved to {os.path.basename(file_path)}")

                # Ask if user wants to open the file
                if messagebox.askyesno("Open File", "Would you like to open the saved plot?"):
                    self.open_file(file_path)
            except Exception as e:
                messagebox.showerror("Save Error", f"Error saving plot: {e}")

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

    def _setup_derivative_tab(self):
        """Set up the derivative tab with two plots for forward and reverse derivatives."""
        # Configure the derivative tab layout
        self.derivative_tab.columnconfigure(0, weight=1)
        self.derivative_tab.rowconfigure(0, weight=1)  # Plot area
        self.derivative_tab.rowconfigure(1, weight=0)  # Control buttons

        # Create plot area
        plot_frame = ttk.LabelFrame(self.derivative_tab, text="Derivative Plot Preview")
        plot_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        # Configure the plot frame
        plot_frame.columnconfigure(0, weight=1)
        plot_frame.columnconfigure(1, weight=1)
        plot_frame.rowconfigure(0, weight=1)

        # Create the plot containers and matplotlib figures
        self.derivative_frames = []
        self.derivative_figures = []
        self.derivative_canvases = []

        titles = ["Forward Sweep Derivative", "Reverse Sweep Derivative"]

        for i in range(2):
            frame = ttk.Frame(plot_frame)
            frame.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)
            self.derivative_frames.append(frame)

            # Create figure and canvas
            fig = Figure(figsize=(4, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.set_title(titles[i])
            ax.set_xlabel("Shear rate (1/s)")
            ax.set_ylabel("dη/dγ̇ (Pa.s²)")
            ax.set_xscale("log")  # X-axis is still logarithmic
            ax.set_yscale("linear")  # Y-axis is linear as requested
            ax.grid(True)
            self.derivative_figures.append(fig)

            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.derivative_canvases.append(canvas)

            # Add save button
            save_btn = ttk.Button(frame, text="Save Plot",
                                  command=lambda idx=i: self._save_derivative_plot(idx))
            save_btn.pack(side=tk.BOTTOM, pady=5)

        # Create button frame with status info
        button_frame = ttk.Frame(self.derivative_tab)
        button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        # Add status label
        self.derivative_status_var = tk.StringVar(value="No data processed yet")
        ttk.Label(button_frame, textvariable=self.derivative_status_var).pack(side=tk.LEFT, padx=5)

    def _calculate_derivative(self, x, y):
        """
        Calculate derivative d(log y)/d(log x) for given data points.

        Args:
            x: Array of x values (shear rate)
            y: Array of y values (viscosity)

        Returns:
            Arrays of original x values and log-log derivative values
        """
        try:
            # Print raw data types for debugging
            print(f"x type: {type(x)}, y type: {type(y)}")

            # Convert inputs to numpy arrays if they aren't already
            x_array = np.asarray(x, dtype=float)
            y_array = np.asarray(y, dtype=float)

            # Sort data by x values
            sorted_indices = np.argsort(x_array)
            x_sorted = x_array[sorted_indices]
            y_sorted = y_array[sorted_indices]

            # Check for non-positive values
            x_positive = x_sorted > 0
            y_positive = y_sorted > 0

            if not np.all(x_positive) or not np.all(y_positive):
                print(f"Warning: Found non-positive values in data.")
                print(f"  Non-positive x values: {np.sum(~x_positive)}")
                print(f"  Non-positive y values: {np.sum(~y_positive)}")

                # Filter out non-positive values
                valid_indices = x_positive & y_positive
                x_sorted = x_sorted[valid_indices]
                y_sorted = y_sorted[valid_indices]

                if len(x_sorted) < 2:
                    print("Not enough valid data points after filtering")
                    return np.array([]), np.array([])

            # Convert to log space
            log_x = np.log10(x_sorted)
            log_y = np.log10(y_sorted)

            # Calculate numerical derivative in log-log space
            dlog_y_dlog_x = np.gradient(log_y, log_x)

            # Debug information
            print(f"Log-log derivative calculation successful:")
            print(f"  Number of points: {len(x_sorted)}")
            print(f"  x range: {min(x_sorted)} to {max(x_sorted)}")
            print(f"  y range: {min(y_sorted)} to {max(y_sorted)}")
            print(f"  Derivative range: {min(dlog_y_dlog_x)} to {max(dlog_y_dlog_x)}")

            return x_sorted, dlog_y_dlog_x
        except Exception as e:
            print(f"Error calculating log-log derivative: {e}")
            import traceback
            traceback.print_exc()
            # Return empty arrays if calculation fails
            return np.array([]), np.array([])

    def _update_forward_derivative(self, file_paths):
        """Update the forward sweep derivative plot."""
        if not isinstance(file_paths, list):
            file_paths = [file_paths]

        # Clear the plot
        ax = self.derivative_figures[0].axes[0]
        ax.clear()

        # Set plot properties
        ax.set_title("Forward Sweep Derivative")
        ax.set_xlabel("Shear rate (1/s)")
        ax.set_ylabel("dη/dγ̇ (Pa.s²)")
        ax.set_xscale("log")
        ax.set_yscale("linear")
        ax.grid(True)

        # Process data and plot
        try:
            if len(file_paths) == 1:
                df, _, _ = self.processor.process_viscosity_single(file_paths[0], "FORWARD")
                forward_data = df[df["Sweep"] == "FORWARD"]

                # Extract data
                x = forward_data["Shear rate"].values
                y = forward_data["Viscosity"].values

                # Calculate derivative
                x_sorted, dy_dx = self._calculate_derivative(x, y)

                # Check if calculation was successful
                if len(x_sorted) > 0:
                    # Plot the derivative
                    label = os.path.basename(file_paths[0]).split('_')[0]
                    ax.plot(x_sorted, dy_dx, 'o-', label=label, color='blue')
                else:
                    self.derivative_status_var.set("Error calculating derivative")
            else:
                # Multiple files
                for i, file_path in enumerate(file_paths):
                    df, _, _ = self.processor.process_viscosity_single(file_path, "FORWARD")
                    forward_data = df[df["Sweep"] == "FORWARD"]

                    # Extract data
                    x = forward_data["Shear rate"].values
                    y = forward_data["Viscosity"].values

                    # Calculate derivative
                    x_sorted, dy_dx = self._calculate_derivative(x, y)

                    # Check if calculation was successful
                    if len(x_sorted) > 0:
                        # Plot the derivative
                        color = plt.cm.tab10(i % 10)
                        label = os.path.basename(file_path).split('_')[0]
                        ax.plot(x_sorted, dy_dx, 'o-', label=label, color=color)

            ax.legend()
            self.derivative_canvases[0].draw()

        except Exception as e:
            print(f"Error updating forward derivative plot: {e}")
            self.derivative_status_var.set("Error updating forward derivative")

    def _update_reverse_derivative(self, file_paths):
        """Update the reverse sweep derivative plot."""
        if not isinstance(file_paths, list):
            file_paths = [file_paths]

        # Clear the plot
        ax = self.derivative_figures[1].axes[0]
        ax.clear()

        # Set plot properties
        ax.set_title("Reverse Sweep Derivative")
        ax.set_xlabel("Shear rate (1/s)")
        ax.set_ylabel("dη/dγ̇ (Pa.s²)")
        ax.set_xscale("log")
        ax.set_yscale("linear")
        ax.grid(True)

        # Process data and plot
        try:
            if len(file_paths) == 1:
                df, _, _ = self.processor.process_viscosity_single(file_paths[0], "REVERSE")
                reverse_data = df[df["Sweep"] == "REVERSE"]

                # Extract data
                x = reverse_data["Shear rate"].values
                y = reverse_data["Viscosity"].values

                # Calculate derivative
                x_sorted, dy_dx = self._calculate_derivative(x, y)

                # Check if calculation was successful
                if len(x_sorted) > 0:
                    # Plot the derivative
                    label = os.path.basename(file_paths[0]).split('_')[0]
                    ax.plot(x_sorted, dy_dx, 'o-', label=label, color='red')
                else:
                    self.derivative_status_var.set("Error calculating derivative")
            else:
                # Multiple files
                for i, file_path in enumerate(file_paths):
                    df, _, _ = self.processor.process_viscosity_single(file_path, "REVERSE")
                    reverse_data = df[df["Sweep"] == "REVERSE"]

                    # Extract data
                    x = reverse_data["Shear rate"].values
                    y = reverse_data["Viscosity"].values

                    # Calculate derivative
                    x_sorted, dy_dx = self._calculate_derivative(x, y)

                    # Check if calculation was successful
                    if len(x_sorted) > 0:
                        # Plot the derivative
                        color = plt.cm.tab10(i % 10)
                        label = os.path.basename(file_path).split('_')[0]
                        ax.plot(x_sorted, dy_dx, 'o-', label=label, color=color)

            ax.legend()
            self.derivative_canvases[1].draw()

        except Exception as e:
            print(f"Error updating reverse derivative plot: {e}")
            self.derivative_status_var.set("Error updating reverse derivative")

    def _save_derivative_plot(self, plot_index):
        """Save the specified derivative plot to a file."""
        # Define plot types for filename
        plot_types = ["forward_derivative", "reverse_derivative"]

        # Create default filename
        default_name = f"viscosity_{plot_types[plot_index]}.png"

        # Ask user where to save the file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=default_name,
            initialdir=self.output_directory
        )

        if file_path:
            try:
                # Save the figure
                self.derivative_figures[plot_index].savefig(file_path, dpi=300, bbox_inches='tight')
                self.derivative_status_var.set(f"Plot saved to {os.path.basename(file_path)}")

                # Ask if user wants to open the file
                if messagebox.askyesno("Open File", "Would you like to open the saved plot?"):
                    self.open_file(file_path)
            except Exception as e:
                messagebox.showerror("Save Error", f"Error saving plot: {e}")
