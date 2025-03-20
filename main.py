from gui import UserInterface
from processor import DataProcessor
import os


def get_output_directory():
    with open("config.txt", "r") as file:
        return file.readline().strip()

def main():
    # Initialize UI and data processor
    ui = UserInterface()
    output_directory = get_output_directory()

    processor = DataProcessor(output_directory)

    ui.display_message(f"Output directory: {output_directory}")

    # Get experiment type
    experiment = ui.get_experiment_type()

    # Get file mode
    mode = ui.get_file_mode()

    if experiment == 'V':
        if mode == 'S':
            plotting_type = input("Normal (N) or derivative (D)? ").strip().upper()
            if plotting_type == 'N':
                # Single file mode
                file_path = ui.select_files(multiple=False)
                ui.display_message(f"Selected file: {file_path}")

                # Get sweep type
                sweep_type = ui.get_sweep_type()

                # Process data
                df, fig_name, full_output_path = processor.process_viscosity_single(file_path, sweep_type)

                # Display results
                ui.display_message(f"Data loaded successfully. Shape: {df.shape}")
                ui.display_message(f"Generating plot: {fig_name}")

                if os.path.exists(full_output_path):
                    ui.display_message(f"Plot saved successfully: {full_output_path}")
                else:
                    ui.display_message(f"Warning: Plot file not found at expected location: {full_output_path}")

            elif plotting_type == 'D':
                # Single file mode
                file_path = ui.select_files(multiple=False)
                ui.display_message(f"Selected file: {file_path}")

                # Get sweep type
                sweep_type = ui.get_sweep_type()

                # Process data
                df, fig_name, full_output_path = processor.process_diff_viscosity_single(file_path, sweep_type)

                # Display results
                ui.display_message(f"Data loaded successfully. Shape: {df.shape}")
                ui.display_message(f"Generating plot: {fig_name}")

                if os.path.exists(full_output_path):
                    ui.display_message(f"Plot saved successfully: {full_output_path}")
                else:
                    ui.display_message(f"Warning: Plot file not found at expected location: {full_output_path}")


        elif mode == 'M':
            # Multiple file mode
            file_paths = ui.select_files(multiple=True)
            ui.display_message(f"Selected {len(file_paths)} files:")
            for path in file_paths:
                ui.display_message(f"  - {path}")

            # Get sweep type
            sweep_type = ui.get_sweep_type()

            # Process data
            dataframes, dataset_names, fig_name, full_output_path = processor.process_viscosity_multiple(file_paths,
                                                                                                         sweep_type)

            # Display results
            ui.display_message(f"Loaded {len(dataframes)} datasets with names: {', '.join(dataset_names)}")
            ui.display_message(f"Generating comparison plot: {fig_name}")

            if os.path.exists(full_output_path):
                ui.display_message(f"Plot saved successfully: {full_output_path}")
            else:
                ui.display_message(f"Warning: Plot file not found at expected location: {full_output_path}")

    if experiment == 'T':
        if mode == 'S':
            # Single file mode
            file_path = ui.select_files(multiple=False)
            ui.display_message(f"Selected file: {file_path}")

            # Process data
            df, fig_name, full_output_path = processor.process_thixotropy_single(file_path)

            # Display results
            ui.display_message(f"Data loaded successfully. Shape: {df.shape}")
            ui.display_message(f"Generating plot: {fig_name}")

            if os.path.exists(full_output_path):
                ui.display_message(f"Plot saved successfully: {full_output_path}")
            else:
                ui.display_message(f"Warning: Plot file not found at expected location: {full_output_path}")

        elif mode == 'M':
            # Multiple file mode
            file_paths = ui.select_files(multiple=True)
            ui.display_message(f"Selected {len(file_paths)} files:")
            for path in file_paths:
                ui.display_message(f"  - {path}")

            # Process data
            dataframes, dataset_names, fig_name, full_output_path = processor.process_thixotropy_multiple(file_paths)

            # Display results
            ui.display_message(f"Loaded {len(dataframes)} datasets with names: {', '.join(dataset_names)}")
            ui.display_message(f"Generating comparison plot: {fig_name}")

            if os.path.exists(full_output_path):
                ui.display_message(f"Plot saved successfully: {full_output_path}")
            else:
                ui.display_message(f"Warning: Plot file not found at expected location: {full_output_path}")

if __name__ == "__main__":
    main()