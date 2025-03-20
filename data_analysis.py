import pandas as pd
from data_import import load_thixotropy_data


def calculate_viscosity_ratio(df):
    """Computes the viscosity recovery ratio (percentage)."""
    eta_preshear = df[df["peak"] == "PRESHEAR"]["Viscosity"].iloc[-1]
    eta_recovery = df[df["peak"] == "RECOVERY"]["Viscosity"].iloc[-1]


    viscosity_ratio = (eta_recovery / eta_preshear) * 100
    print(f"Viscosity Ratio")
    print(f"viscosity pre-shear: {eta_preshear}")
    print(f"viscosity recovery: {eta_recovery}")
    print(f"viscosity ratio: {viscosity_ratio}")


    return viscosity_ratio


def calculate_structural_recovery(df):
    """Computes structural recovery percentage."""
    eta_preshear = df[df["peak"] == "PRESHEAR"]["Viscosity"].iloc[-1]
    eta_highshear = df[df["peak"] == "HIGHSHEAR"]["Viscosity"].iloc[-1]
    eta_recovery = df[df["peak"] == "RECOVERY"]["Viscosity"].iloc[-1]

    return ((eta_recovery - eta_highshear) / (eta_preshear - eta_highshear)) * 100


def calculate_thixotropic_index(df):
    """Computes thixotropic index (ratio of low shear to high shear viscosity)."""
    eta_preshear = df[df["peak"] == "PRESHEAR"]["Viscosity"].iloc[-1]
    eta_highshear = df[df["peak"] == "HIGHSHEAR"]["Viscosity"].iloc[-1]

    thixotropic_index = eta_preshear / eta_highshear

    print(f"Thixotropic Index")
    print(f"viscosity low shear: {eta_preshear}")
    print(f"viscosity high shear: {eta_highshear}")
    print(f"Thixotropic index: {thixotropic_index}")


    return thixotropic_index


def calculate_80_percent_viscosity_recovery(df):

    preshear_df = df[df["peak"] == "PRESHEAR"]
    recovery_df = df[df["peak"] == "RECOVERY"].copy()  # Create an explicit copy

    eta_preshear = preshear_df["Viscosity"].iloc[-1]
    eta_recovery_80_percent = eta_preshear * 0.8

    # Ensure Viscosity column is numeric
    recovery_df["Viscosity"] = pd.to_numeric(recovery_df["Viscosity"], errors='coerce')

    # Filter out any NaN values that might have been created
    recovery_df = recovery_df.dropna(subset=["Viscosity"])

    # Find the closest viscosity value to 80% recovery
    recovery_df["viscosity_diff"] = abs(recovery_df["Viscosity"] - eta_recovery_80_percent)

    # Find the index of the minimum difference
    closest_match_idx = recovery_df["viscosity_diff"].idxmin()

    # Get the time corresponding to the closest viscosity value
    recovery_time_80_percent = recovery_df.loc[closest_match_idx, "Step time"]

    print(f"Slurry Recovery")
    print(f"Recovery Time: {recovery_time_80_percent}")


    return recovery_time_80_percent

def analyze_thixotropy(filepath):
    """Loads data and computes all thixotropy metrics."""
    df = load_thixotropy_data(filepath)

    results = {
        "Viscosity Ratio (%)": calculate_viscosity_ratio(df),
        "Thixotropic Index": calculate_thixotropic_index(df),
        "80% Recovery Time": calculate_80_percent_viscosity_recovery(df),
    }

    return results
