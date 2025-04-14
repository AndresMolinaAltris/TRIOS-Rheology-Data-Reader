import matplotlib.pyplot as plt
import os
import numpy as np


def plot_viscosity_data(df, fig_name, export_path, sweep_types=None, datasets=None, colors=None, markers=None):
    """
    Plots viscosity data for one or multiple datasets and sweep types.

    Parameters:
    df (pd.DataFrame or list): DataFrame(s) containing sweep data.
    fig_name (str): Filename for the exported plot.
    export_path (str): Directory where the plot will be saved.
    sweep_types (str or list): "FORWARD", "REVERSE", or a list of both. Default: all available.
    datasets (list): Names for each dataset. Default: "Dataset" or "Dataset 1", "Dataset 2", etc.
    colors (list): Colors for plots. Default: matplotlib default colors.
    markers (list): Markers for plots. Default: matplotlib default markers.
    """
    x_col, y_col = "Shear rate", "Viscosity"

    # Convert single DataFrame to list
    if not isinstance(df, list):
        df = [df]

    # Set default dataset names
    if datasets is None:
        datasets = ["Dataset"] if len(df) == 1 else [f"Dataset {i + 1}" for i in range(len(df))]

    # Set default visual attributes
    colors = plt.cm.tab10.colors if colors is None else colors
    markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h'] if markers is None else markers

    # Create plot
    plt.figure(figsize=(10, 8))
    all_labels = []
    all_handles = []

    # Added this to pass the dataset as an entire string and not a character
    if isinstance(datasets, str):
        datasets = [datasets.split('_')[0]]  # Take first part before underscore
    elif datasets is not None:
        datasets = [d.split('_')[0] for d in datasets]  # Process each dataset name

    # Plot each dataset
    for i, (data, dataset_name) in enumerate(zip(df, datasets)):
        # Determine which sweeps to plot
        available_sweeps = data["Sweep"].unique()
        sweep_list = available_sweeps if sweep_types is None else \
            [sweep_types] if isinstance(sweep_types, str) else sweep_types
        # Plot each sweep
        for j, sweep in enumerate(sweep_list):
            if sweep not in available_sweeps:
                continue

            # Filter data
            selected_data = data[data["Sweep"] == sweep]

            # Set visual attributes
            color_idx = (i * len(sweep_list) + j) % len(colors)
            marker_idx = (i * len(sweep_list) + j) % len(markers)

            # Create label based on context
            if len(df) == 1:
                if len(sweep_list) == 1:
                    label = dataset_name  # For single dataset, just the dataset name
                else:
                    label = f"{sweep} Sweep"  # If multiple sweeps, add sweep type to label
            else:
                label = f"{dataset_name} - {sweep} Sweep"  # Multiple datasets with sweep types

            # Plot data
            scatter = plt.scatter(
                selected_data[x_col],
                selected_data[y_col],
                label=label,
                color=colors[color_idx],
                marker=markers[marker_idx],
                alpha=0.7,
                s=50
            )

            all_handles.append(scatter)
            all_labels.append(label)

    # Set plot attributes
    plt.xlabel(f"{x_col} (1/s)")
    plt.ylabel(f"{y_col} (Pa.s)")
    plt.xscale("log")
    plt.yscale("log")
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)

    # Add legend
    if all_labels:
        plt.legend(all_handles, all_labels, loc='best', framealpha=0.7)

    # Save the figure
    os.makedirs(export_path, exist_ok=True)
    plt.savefig(os.path.join(export_path, fig_name), dpi=300, bbox_inches="tight")
    plt.close()


def plot_diff_viscosity_data(df, fig_name, export_path, sweep_types=None, datasets=None, colors=None, markers=None):
    """
    Plots viscosity data and its derivative for one or multiple datasets and sweep types.
    """
    x_col, y_col = "Shear rate", "Viscosity"

    # Convert single DataFrame to list
    if not isinstance(df, list):
        df = [df]

    # Set default dataset names
    if datasets is None:
        datasets = ["Dataset"] if len(df) == 1 else [f"Dataset {i + 1}" for i in range(len(df))]

    # Set default visual attributes
    colors = plt.cm.tab10.colors if colors is None else colors
    markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h'] if markers is None else markers

    # Create figure
    fig, ax1 = plt.subplots(figsize=(10, 8))
    ax2 = ax1.twinx()  # Create second y-axis for derivative

    all_labels = []
    all_handles = []

    # Plot each dataset
    for i, (data, dataset_name) in enumerate(zip(df, datasets)):
        available_sweeps = data["Sweep"].unique()
        sweep_list = available_sweeps if sweep_types is None else \
            [sweep_types] if isinstance(sweep_types, str) else sweep_types

        for j, sweep in enumerate(sweep_list):
            if sweep not in available_sweeps:
                continue

            selected_data = data[data["Sweep"] == sweep]
            selected_data = selected_data.sort_values(by=x_col)

            # Compute derivative (d(viscosity)/d(shear rate))
            shear_rate = selected_data[x_col].values
            viscosity = selected_data[y_col].values

            if len(shear_rate) > 1:
                d_viscosity = np.gradient(viscosity, shear_rate)
            else:
                d_viscosity = np.zeros_like(shear_rate)

            # Set visual attributes
            color_idx = (i * len(sweep_list) + j) % len(colors)
            marker_idx = (i * len(sweep_list) + j) % len(markers)

            label = f"{dataset_name} - {sweep} Sweep"

            # Plot viscosity
            scatter = ax1.scatter(
                shear_rate, viscosity, label=label, color=colors[color_idx],
                marker=markers[marker_idx], alpha=0.7, s=50
            )
            all_handles.append(scatter)
            all_labels.append(label)

            # Plot derivative
            ax2.plot(
                shear_rate, d_viscosity, linestyle='--', color=colors[color_idx],
                alpha=0.7, label=f"dVisc/dShear ({dataset_name} - {sweep})"
            )

    # Set plot attributes
    ax1.set_xlabel(f"{x_col} (1/s)")
    ax1.set_ylabel(f"{y_col} (Pa.s)", color='b')
    ax2.set_ylabel("d(Viscosity)/d(Shear rate) (Pa.s²)", color='r')
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.grid(True, which="both", linestyle="--", linewidth=0.5)

    # Add legends
    ax1.legend(all_handles, all_labels, loc='best', framealpha=0.7)

    # Save the figure
    os.makedirs(export_path, exist_ok=True)
    plt.savefig(os.path.join(export_path, fig_name), dpi=300, bbox_inches="tight")
    plt.close()


def plot_thixotropy_data(df_list, fig_name, export_path, datasets=None, colors=None, markers=None):
    """
    Plots viscosity vs time for one or multiple thixotropy datasets.

    Parameters:
    df_list (list of pd.DataFrame): A single or a list of DataFrames containing thixotropy data.
    fig_name (str): Filename for the exported plot.
    export_path (str): Directory where the plot will be saved.
    datasets (list): Names for each dataset. Default: "Dataset 1", "Dataset 2", etc.
    colors (list): Colors for plots. Default: matplotlib default colors.
    markers (list): Markers for plots. Default: predefined markers.
    """
    if not isinstance(df_list, list):
        df_list = [df_list]

    if datasets is None:
        datasets = [f"Dataset {i + 1}" for i in range(len(df_list))]

    colors = plt.cm.tab10.colors if colors is None else colors
    markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h'] if markers is None else markers

    plt.figure(figsize=(10, 8))

    # Added this to pass the dataset as an entire string and not a character
    if isinstance(datasets, str):
        datasets = [datasets.split('_')[0]]
    elif datasets is not None:
        datasets = [d.split('_')[0] for d in datasets]

    for i, (df, dataset_name) in enumerate(zip(df_list, datasets)):
        if "Time" not in df.columns or "Viscosity" not in df.columns:
            raise ValueError(f"Dataset {dataset_name} is missing required columns: 'Time' and 'Viscosity'")

        plt.scatter(
            df["Time"], df["Viscosity"],
            label=dataset_name,
            color=colors[i % len(colors)],
            marker=markers[i % len(markers)],
            alpha=0.7,
            s=5
        )

    plt.xlabel("Time (s)")
    plt.ylabel("Viscosity (Pa.s)")
    plt.yscale("log")
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.legend(loc='best', framealpha=0.7)

    os.makedirs(export_path, exist_ok=True)
    plt.savefig(os.path.join(export_path, fig_name), dpi=300, bbox_inches="tight")
    plt.close()