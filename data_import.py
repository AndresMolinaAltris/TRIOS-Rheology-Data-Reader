import pandas as pd
import numpy as np

# Load viscosity data
def load_viscosity_stress_data(filepath):
    """
    Reads shear viscosity data from an Excel file.

    This function reads two sheets, 'Flow sweep - 1' and 'Flow sweep - 2',
    verifies their existence, removes the unit row, adds a 'Sweep' column to
    indicate direction, and merges both into a single DataFrame.

    Parameters:
    filepath (str): Path to the Excel file.

    Returns:
    pd.DataFrame: Merged DataFrame containing both forward and reverse sweeps.

    Raises:
    FileNotFoundError: If the file does not exist.
    ValueError: If the required sheets are missing or if the data format is incorrect.
    """

    # Check if the file is the correct type of file (*.xls)
    try:
        xls = pd.ExcelFile(filepath, engine="xlrd")
    except Exception as e:
        raise ValueError(f"Error: Unable to read the file '{filepath}'. Ensure it is a valid Excel (.xls) file.\n{e}")

    # Check if the required sheets exist
    required_sheets = ["Flow sweep - 1", "Flow sweep - 2"]
    missing_sheets = [sheet for sheet in required_sheets if sheet not in xls.sheet_names]

    if missing_sheets:
        raise ValueError(f"Error: The file '{filepath}' is missing required sheets: {missing_sheets}")

    # Read and process forward sweep data
    forward_df = pd.read_excel(xls, sheet_name="Flow sweep - 1", header=1)
    forward_df = forward_df[1:].reset_index(drop=True)  # Remove units row
    forward_df["Sweep"] = "FORWARD"

    # Read and process reverse sweep data
    reverse_df = pd.read_excel(xls, sheet_name="Flow sweep - 2", header=1)
    reverse_df = reverse_df[1:].reset_index(drop=True)  # Remove units row
    reverse_df["Sweep"] = "REVERSE"

    # Merge both DataFrames
    merged_df = pd.concat([forward_df, reverse_df], ignore_index=True)

    return merged_df


# Load thixotropy data
def load_thixotropy_data(filepath):
    """
       Load and process thixotropy data from an Excel (.xls) file.

       This function reads data from an Excel file containing three required sheets:
       "Peak hold - 1", "Peak hold - 2", and "Peak hold - 3". It checks for the
       presence of these sheets, extracts the data while removing unit rows,
       labels each dataset accordingly, and merges them into a single DataFrame.
       A total time column is also added.

       Parameters:
       filepath (str): Path to the Excel (.xls) file.

       Returns:
       pandas.DataFrame: A merged DataFrame containing thixotropy data with
                         labeled peak phases and a calculated time column.

       Raises:
       ValueError: If the file is not a valid Excel (.xls) file or if required
                   sheets are missing.
       """

    # Check if the file selected is the correct type of file (*.xls)
    try:
        xls = pd.ExcelFile(filepath, engine="xlrd")
    except Exception as e:
        raise ValueError(f"Error: Unable to read the file '{filepath}'. Ensure it is a valid Excel (.xls) file.\n{e}")

    # Check if the required sheets exist
    required_sheets = ["Peak hold - 1", "Peak hold - 2", "Peak hold - 3"]
    missing_sheets = [sheet for sheet in required_sheets if sheet not in xls.sheet_names]

    if missing_sheets:
        raise ValueError(f"Error: The file '{filepath}' is missing required sheets: {missing_sheets}")

    # Read and process Peak hold - 1  data
    preshear_df = pd.read_excel(xls, sheet_name="Peak hold - 1", header=1)
    preshear_df = preshear_df[1:].reset_index(drop=True)  # Remove units row
    preshear_df["peak"] = "PRESHEAR"

    # Read and process Peak hold - 2  data
    highshear_df = pd.read_excel(xls, sheet_name="Peak hold - 2", header=1)
    highshear_df = highshear_df[1:].reset_index(drop=True)  # Remove units row
    highshear_df["peak"] = "HIGHSHEAR"

    # Read and process Peak hold - 3  data
    recovery_df = pd.read_excel(xls, sheet_name="Peak hold - 3", header=1)
    recovery_df = recovery_df[1:].reset_index(drop=True)  # Remove units row
    recovery_df["peak"] = "RECOVERY"

    # Merge both DataFrames
    merged_df = pd.concat([preshear_df, highshear_df, recovery_df], ignore_index=True)

    # Add a total time column
    merged_df['Time'] = np.arange(0, len(merged_df) * 0.1, 0.1)

    return merged_df



