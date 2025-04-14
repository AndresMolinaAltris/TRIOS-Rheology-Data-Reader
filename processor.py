from data_import import *
from plotting import *
from data_analysis import calculate_viscosity_ratio, calculate_thixotropic_index, \
    calculate_80_percent_viscosity_recovery, calculate_structural_recovery
import pandas as pd
import re
import os


class DataProcessor:
    def __init__(self, output_directory):
        """
        Initialize the DataProcessor class.

        Parameters:
        output_directory (str): Directory where processed data and plots will be saved.
        """

        self.output_directory = output_directory
        os.makedirs(self.output_directory, exist_ok=True)

    def process_viscosity_single(self, file_path, sweep_type):
        """
        Process a single viscosity data file and generate a plot.

        Parameters:
        file_path (str): Path to the viscosity data file.
        sweep_type (str or list): Type of sweep (e.g., 'up', 'down', or ['up', 'down']).

        Returns:
        tuple: DataFrame containing processed data, filename of the generated plot, full path of the output file.
        """
        # Load data
        df = load_viscosity_stress_data(file_path)

        # Generate filename
        fig_name = os.path.splitext(os.path.basename(file_path))[0]
        if isinstance(sweep_type, list):
            fig_name += "-BOTH.png"
        else:
            fig_name += f"-{sweep_type}.png"

        # Full path for output file
        full_output_path = os.path.join(self.output_directory, fig_name)

        # Name of the dataset
        name = re.split('[-_]', fig_name)[0]

        # Plot data
        plot_viscosity_data(
            df=df,
            fig_name=fig_name,
            export_path=self.output_directory,
            sweep_types=sweep_type,
            datasets=name
        )

        return df, fig_name, full_output_path

    def process_viscosity_multiple(self, file_paths, sweep_type):
        """
        Process multiple viscosity data files and generate a comparative plot.

        Parameters:
        file_paths (list of str): List of paths to viscosity data files.
        sweep_type (str or list): Type of sweep (e.g., 'up', 'down', or ['up', 'down']).

        Returns:
        tuple: List of DataFrames, list of dataset names, filename of the generated plot, full path of the output file.
        """
        # Load all datasets
        dataframes = []
        dataset_names = []

        for file_path in file_paths:
            df = load_viscosity_stress_data(file_path)
            dataframes.append(df)

            # Use filename as dataset name
            name = os.path.splitext(os.path.basename(file_path))[0].split('_')[0]
            dataset_names.append(name)

        # Generate filename
        fig_name = "comparison"
        if isinstance(sweep_type, list):
            fig_name += "-BOTH.png"
        else:
            fig_name += f"-{sweep_type}.png"

        # Full path for output file
        full_output_path = os.path.join(self.output_directory, fig_name)

        # Plot data
        plot_viscosity_data(
            df=dataframes,
            fig_name=fig_name,
            export_path=self.output_directory,
            sweep_types=sweep_type,
            datasets=dataset_names
        )

        return dataframes, dataset_names, fig_name, full_output_path

    def process_diff_viscosity_single(self, file_path, sweep_type):
        """
        Process a single differential viscosity data file and generate a plot.

        Parameters:
        file_path (str): Path to the viscosity data file.
        sweep_type (str or list): Type of sweep (e.g., 'up', 'down', or ['up', 'down']).

        Returns:
        tuple: DataFrame containing processed data, filename of the generated plot, full path of the output file.
        """
        # Load data
        df = load_viscosity_stress_data(file_path)

        # Generate filename
        fig_name = os.path.splitext(os.path.basename(file_path))[0]
        if isinstance(sweep_type, list):
            fig_name += "-BOTH.png"
        else:
            fig_name += f"-{sweep_type}.png"

        # Full path for output file
        full_output_path = os.path.join(self.output_directory, fig_name)

        # Plot data
        plot_diff_viscosity_data(
            df=df,
            fig_name=fig_name,
            export_path=self.output_directory,
            sweep_types=sweep_type
        )

        return df, fig_name, full_output_path

    def process_thixotropy_single(self, file_path):
        """
        Process a single thixotropy data file and generate a plot.

        Parameters:
        file_path (str): Path to the thixotropy data file.

        Returns:
        tuple: DataFrame containing processed data, filename of the generated plot, full path of the output file.
        """
        # Load data
        df = load_thixotropy_data(file_path)

        # Generate filename
        fig_name = os.path.splitext(os.path.basename(file_path))[0]

        # Full path for output file. Added a png extension
        full_output_path = os.path.join(self.output_directory, fig_name + ".png")

        # Name of the dataset
        name = re.split('[-_]', fig_name)[0]

        # Plot data
        plot_thixotropy_data(
            df_list=df,
            fig_name=fig_name,
            export_path=self.output_directory,
            datasets=name
        )

        return df, fig_name, full_output_path

    def process_thixotropy_multiple(self, file_paths):
        """
        Process multiple thixotropy data files and generate a comparative plot.

        Parameters:
        file_paths (list of str): List of paths to thixotropy data files.

        Returns:
        tuple: List of DataFrames, list of dataset names, filename of the generated plot, full path of the output file.
        """
        # Load all datasets
        dataframes = []
        dataset_names = []

        for file_path in file_paths:
            df = load_thixotropy_data(file_path)
            dataframes.append(df)

            # Use filename as dataset name
            name = os.path.splitext(os.path.basename(file_path))[0]
            dataset_names.append(name)

        # Generate filename
        fig_name = "comparison"

        # Full path for output file. Added the png extension
        full_output_path = os.path.join(self.output_directory, fig_name + ".png")
        print(full_output_path)

        # Plot data
        plot_thixotropy_data(
            df_list=dataframes,
            fig_name=fig_name,
            export_path=self.output_directory,
            datasets=dataset_names
        )

        return dataframes, dataset_names, fig_name, full_output_path

    # ================ ANALYSIS METHODS ================

    def calculate_thixotropy_metrics(self, df):
        """
        Calculate all thixotropy metrics for a given DataFrame.

        Parameters:
        df (pd.DataFrame): DataFrame containing thixotropy data with labeled peaks.

        Returns:
        dict: Dictionary containing all calculated metrics.
        """
        try:
            # Check if the DataFrame has the necessary structure
            required_columns = ["Viscosity", "peak", "Step time"]
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                raise ValueError(f"Data is missing required columns: {', '.join(missing_columns)}")

            required_peaks = ["PRESHEAR", "HIGHSHEAR", "RECOVERY"]
            available_peaks = df["peak"].unique()
            missing_peaks = [peak for peak in required_peaks if peak not in available_peaks]

            if missing_peaks:
                raise ValueError(f"Data is missing required phases: {', '.join(missing_peaks)}")

            # Calculate all metrics
            viscosity_ratio = calculate_viscosity_ratio(df)
            thixotropic_index = calculate_thixotropic_index(df)
            recovery_time_80_percent = calculate_80_percent_viscosity_recovery(df)
            structural_recovery = calculate_structural_recovery(df)

            # Return a dictionary of results
            return {
                "Viscosity Ratio (%)": viscosity_ratio,
                "Thixotropic Index": thixotropic_index,
                "80% Recovery Time (s)": recovery_time_80_percent,
                "Structural Recovery (%)": structural_recovery
            }

        except Exception as e:
            # Handle errors by returning a dict with error message
            return {"Error": str(e)}

    def analyze_thixotropy_single(self, file_path):
        """
        Load thixotropy data from a file and calculate all metrics.

        Parameters:
        file_path (str): Path to the thixotropy data file.

        Returns:
        tuple: (DataFrame with the data, dict with the results)
        """
        try:
            # Load the data
            df = load_thixotropy_data(file_path)

            # Calculate metrics
            results = self.calculate_thixotropy_metrics(df)

            return df, results

        except Exception as e:
            return None, {"Error": f"Failed to analyze file: {str(e)}"}

    def analyze_thixotropy_multiple(self, file_paths):
        """
        Load and analyze multiple thixotropy data files.

        Parameters:
        file_paths (list): List of paths to thixotropy data files.

        Returns:
        dict: Dictionary mapping sample names to their results dictionaries.
        """
        all_results = {}

        for file_path in file_paths:
            try:
                # Extract sample name from file path
                sample_name = os.path.splitext(os.path.basename(file_path))[0]

                # Load and analyze data
                df, results = self.analyze_thixotropy_single(file_path)

                # Store results with sample name as key
                all_results[sample_name] = results

            except Exception as e:
                all_results[os.path.basename(file_path)] = {"Error": f"Failed to analyze file: {str(e)}"}

        return all_results

    # ================ EXPORT METHODS ================

    def export_thixotropy_results_single(self, results, file_path, export_format='csv'):
        """
        Export thixotropy analysis results for a single file to CSV or Excel.

        Parameters:
        results (dict): Dictionary containing metric names and values
        file_path (str): Path to save the exported file
        export_format (str): Format to export ('csv' or 'excel')

        Returns:
        tuple: (Success flag, message or error)
        """
        try:
            # Create a DataFrame from the results
            metrics_df = pd.DataFrame(list(results.items()), columns=['Metric', 'Value'])

            # Export based on the requested format
            if export_format.lower() == 'csv':
                metrics_df.to_csv(file_path, index=False)
                return True, file_path
            elif export_format.lower() == 'excel':
                try:
                    # Try to use to_excel directly (works with openpyxl as default engine)
                    metrics_df.to_excel(file_path, index=False, sheet_name='Thixotropy Metrics')
                    return True, file_path
                except Exception as excel_error:
                    print(f"Excel export error: {str(excel_error)}")
                    # Fallback to CSV if Excel export fails
                    csv_path = os.path.splitext(file_path)[0] + ".csv"
                    metrics_df.to_csv(csv_path, index=False)
                    return True, f"Exported as CSV to {csv_path} (Excel export failed)"
            else:
                return False, f"Unsupported export format: {export_format}"

        except Exception as e:
            return False, f"Export failed: {str(e)}"

    def export_thixotropy_results_multiple(self, all_results, file_path, export_format='csv'):
        """
        Export thixotropy analysis results for multiple files to CSV or Excel.

        Parameters:
        all_results (dict): Dictionary mapping sample names to result dictionaries
        file_path (str): Path to save the exported file
        export_format (str): Format to export ('csv' or 'excel')

        Returns:
        tuple: (Success flag, message or error)
        """
        try:
            # First, create a unified data structure
            # Get all possible metrics from all samples
            all_metrics = set()
            for sample_results in all_results.values():
                all_metrics.update(sample_results.keys())

            # Create a DataFrame with samples as rows and metrics as columns
            data = []
            for sample, results in all_results.items():
                row = {'Sample': sample}
                for metric in all_metrics:
                    row[metric] = results.get(metric, None)
                data.append(row)

            metrics_df = pd.DataFrame(data)

            # Also create long format for potential Excel export
            long_data = []
            for sample, results in all_results.items():
                for metric, value in results.items():
                    long_data.append({
                        'Sample': sample,
                        'Metric': metric,
                        'Value': value
                    })

            long_df = pd.DataFrame(long_data)

            # Export based on the requested format
            if export_format.lower() == 'csv':
                # For CSV, just export the wide format
                metrics_df.to_csv(file_path, index=False)
                return True, file_path
            elif export_format.lower() == 'excel':
                try:
                    # Try to use ExcelWriter with xlsxwriter
                    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                        # Wide format
                        metrics_df.to_excel(writer, sheet_name='Metrics Summary', index=False)
                        # Long format (for easier plotting)
                        long_df.to_excel(writer, sheet_name='Metrics Detail', index=False)
                    return True, file_path
                except Exception as excel_error:
                    print(f"Excel export error: {str(excel_error)}")
                    # Fallback to CSV if Excel export fails
                    csv_path = os.path.splitext(file_path)[0] + ".csv"
                    metrics_df.to_csv(csv_path, index=False)
                    return True, f"Exported as CSV to {csv_path} (Excel export failed)"
            else:
                return False, f"Unsupported export format: {export_format}"

        except Exception as e:
            return False, f"Export failed: {str(e)}"