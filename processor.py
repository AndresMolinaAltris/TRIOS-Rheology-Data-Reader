from data_import import *
from plotting import *
import re


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
            name = os.path.splitext(os.path.basename(file_path))[0]
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

        # Full path for output file
        full_output_path = os.path.join(self.output_directory, fig_name)

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

        # Full path for output file
        full_output_path = os.path.join(self.output_directory, fig_name)

        # Plot data
        plot_thixotropy_data(
            df_list=dataframes,
            fig_name=fig_name,
            export_path=self.output_directory,
            datasets=dataset_names
        )

        return dataframes, dataset_names, fig_name, full_output_path