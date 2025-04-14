import tkinter as tk
from tkinter import ttk, filedialog
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class FileSelector(ttk.Frame):
    """A component that combines file selection and plot display."""

    def __init__(self, parent, initial_dir=None):
        """
        Initialize the viscosity analyzer component.

        Args:
            parent: The parent widget
            initial_dir (str, optional): Initial directory to browse
        """
        super().__init__(parent)

        self.initial_dir = initial_dir or os.getcwd()
        self.current_dir = tk.StringVar(value=self.initial_dir)
        self.selected_files = []  # Full paths of selected files
        self.status_var = tk.StringVar(value="No files selected")

        self._create_widgets()
        self._update_file_list()

    def _create_widgets(self):
        """Create all widgets for the file selector and plot area."""
        # Configure grid layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)  # Directory selection
        self.rowconfigure(1, weight=0)  # File lists (fixed height)
        self.rowconfigure(2, weight=1)  # Plot area (expands)
        self.rowconfigure(3, weight=0)  # Button area

        # Directory selection
        dir_frame = ttk.Frame(self)
        dir_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        ttk.Label(dir_frame, text="Directory:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(dir_frame, textvariable=self.current_dir, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True,
                                                                           padx=(0, 5))
        ttk.Button(dir_frame, text="Browse...", command=self._browse_directory).pack(side=tk.LEFT)

        # File lists area
        file_frame = ttk.Frame(self)
        file_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        file_frame.columnconfigure(0, weight=1)
        file_frame.columnconfigure(1, weight=0)
        file_frame.columnconfigure(2, weight=1)

        # Available files list (left)
        avail_frame = ttk.LabelFrame(file_frame, text="Available XLS Files")
        avail_frame.grid(row=0, column=0, sticky="ew")

        avail_scrollbar = ttk.Scrollbar(avail_frame)
        avail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.available_listbox = tk.Listbox(avail_frame, height=6,
                                            selectmode=tk.EXTENDED,
                                            yscrollcommand=avail_scrollbar.set)
        self.available_listbox.pack(fill=tk.BOTH, expand=True)
        avail_scrollbar.config(command=self.available_listbox.yview)

        # Add/Remove buttons (middle)
        button_frame = ttk.Frame(file_frame)
        button_frame.grid(row=0, column=1, sticky="ns", padx=5)

        ttk.Button(button_frame, text=">>", command=self._add_selected_files).pack(pady=5)
        ttk.Button(button_frame, text="<<", command=self._remove_selected_files).pack(pady=5)

        # Selected files list (right)
        selected_frame = ttk.LabelFrame(file_frame, text="Selected Files")
        selected_frame.grid(row=0, column=2, sticky="ew")

        sel_scrollbar = ttk.Scrollbar(selected_frame)
        sel_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.selected_listbox = tk.Listbox(selected_frame, height=6,
                                           selectmode=tk.EXTENDED,
                                           yscrollcommand=sel_scrollbar.set)
        self.selected_listbox.pack(fill=tk.BOTH, expand=True)
        sel_scrollbar.config(command=self.selected_listbox.yview)

        # Plot area - three plots side by side
        self.plot_frame = ttk.LabelFrame(self, text="Plot Preview")
        self.plot_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # Create figures and canvases for the three plots
        self._create_plot_area()

        # Button area
        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

        ttk.Label(button_frame, textvariable=self.status_var).pack(side=tk.LEFT)

        ttk.Button(button_frame, text="Process and Plot",
                   command=self._process_files).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Clear Selection",
                   command=self._clear_selection).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Exit",
                   command=lambda: self.master.destroy()).pack(side=tk.RIGHT, padx=5)

    def _create_plot_area(self):
        """Create the three plot areas."""
        # Configure the plot frame for three plots
        self.plot_frame.columnconfigure(0, weight=1)
        self.plot_frame.columnconfigure(1, weight=1)
        self.plot_frame.columnconfigure(2, weight=1)
        self.plot_frame.rowconfigure(0, weight=1)

        # Create sub-frames for each plot
        self.plot_frames = []
        self.figures = []
        self.canvases = []

        plot_titles = ["Forward Sweep", "Reverse Sweep", "Both Sweeps"]

        for i in range(3):
            # Create a frame for this plot
            frame = ttk.Frame(self.plot_frame)
            frame.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)
            self.plot_frames.append(frame)

            # Create figure and canvas
            fig = Figure(figsize=(4, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.set_title(plot_titles[i])
            ax.set_xlabel("Shear rate (1/s)")
            ax.set_ylabel("Viscosity (Pa.s)")
            ax.grid(True)
            self.figures.append(fig)

            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.canvases.append(canvas)

            # Add a save button for this plot
            save_btn = ttk.Button(frame, text="Save Plot",
                                  command=lambda idx=i: self._save_plot(idx))
            save_btn.pack(side=tk.BOTTOM, pady=5)

    def _browse_directory(self):
        """Open a dialog to browse for a directory."""
        dir_path = filedialog.askdirectory(initialdir=self.current_dir.get())
        if dir_path:
            self.current_dir.set(dir_path)
            self._update_file_list()

    def _update_file_list(self):
        """Update the available files listbox with XLS files from the current directory."""
        self.available_listbox.delete(0, tk.END)
        try:
            xls_files = [f for f in os.listdir(self.current_dir.get())
                         if f.lower().endswith('.xls')]
            xls_files.sort()
            for file in xls_files:
                self.available_listbox.insert(tk.END, file)
        except Exception as e:
            print(f"Error listing directory: {e}")

    def _add_selected_files(self):
        """Add selected files from available list to selected list."""
        selected_indices = self.available_listbox.curselection()
        for i in selected_indices:
            file_name = self.available_listbox.get(i)
            full_path = os.path.join(self.current_dir.get(), file_name)

            if full_path not in self.selected_files:
                self.selected_files.append(full_path)
                self.selected_listbox.insert(tk.END, file_name)

        # Update status
        self._update_status()

    def _remove_selected_files(self):
        """Remove selected files from the selected list."""
        selected_indices = self.selected_listbox.curselection()
        for i in sorted(selected_indices, reverse=True):
            file_name = self.selected_listbox.get(i)
            full_path = os.path.join(self.current_dir.get(), file_name)

            if full_path in self.selected_files:
                self.selected_files.remove(full_path)
            self.selected_listbox.delete(i)

        # Update status
        self._update_status()

    def _clear_selection(self):
        """Clear all selected files."""
        self.selected_files = []
        self.selected_listbox.delete(0, tk.END)
        self._update_status()

    def _update_status(self):
        """Update the status text."""
        file_count = len(self.selected_files)
        if file_count == 0:
            self.status_var.set("No files selected")
        elif file_count == 1:
            self.status_var.set("1 file selected")
        else:
            self.status_var.set(f"{file_count} files selected")

    def _process_files(self):
        """Process the selected files and display plots."""
        if not self.selected_files:
            tk.messagebox.showwarning("No Files", "Please select at least one file to process.")
            return

        # In a real implementation, you'd process the files here
        # For now, just update the status and show placeholders
        self.status_var.set(f"Processed {len(self.selected_files)} files")

        # Clear and update plots
        for i, fig in enumerate(self.figures):
            ax = fig.axes[0]
            ax.clear()

            # Set plot properties
            titles = ["Forward Sweep", "Reverse Sweep", "Both Sweeps"]
            ax.set_title(titles[i])
            ax.set_xlabel("Shear rate (1/s)")
            ax.set_ylabel("Viscosity (Pa.s)")

            # Add placeholder data
            x = [0.1, 1, 10, 100, 1000]
            y = [100, 10, 1, 0.1, 0.01]

            if i == 0:  # Forward sweep
                ax.loglog(x, y, 'bo-', label='Forward')
            elif i == 1:  # Reverse sweep
                ax.loglog(x, [y[4 - j] for j in range(5)], 'ro-', label='Reverse')
            else:  # Both sweeps
                ax.loglog(x, y, 'bo-', label='Forward')
                ax.loglog(x, [y[4 - j] for j in range(5)], 'ro-', label='Reverse')

            ax.grid(True)
            ax.legend()

            # Redraw canvas
            self.canvases[i].draw()

    def _save_plot(self, plot_index):
        """Save the selected plot to a file."""
        # Get the figure to save
        fig = self.figures[plot_index]

        # Ask for save location
        file_types = [("PNG files", "*.png"),
                      ("PDF files", "*.pdf"),
                      ("All files", "*.*")]

        plot_types = ["forward", "reverse", "both"]
        default_name = f"viscosity_{plot_types[plot_index]}.png"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=file_types,
            initialfile=default_name
        )

        if file_path:
            try:
                fig.savefig(file_path, dpi=300, bbox_inches='tight')
                self.status_var.set(f"Plot saved to {file_path}")
            except Exception as e:
                tk.messagebox.showerror("Save Error", f"Error saving plot: {e}")


# For testing the component independently
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Viscosity Analyzer Test")
    root.geometry("1000x800")

    # Create and pack the analyzer
    analyzer = ViscosityAnalyzer(root)
    analyzer.pack(fill=tk.BOTH, expand=True)

    root.mainloop()