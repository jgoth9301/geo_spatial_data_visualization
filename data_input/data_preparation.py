import os
import pandas as pd

def prepare_energy_data():
    # Determine the base directory of the current script
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Define input and output paths relative to the base directory
    input_path = os.path.join(base_dir, "energy-data-master", "owid-energy-data.csv")
    output_path = os.path.join(base_dir, "data_preparation.csv")

    # Debug: Print the resolved paths
    print(f"Input path: {input_path}")
    print(f"Output path: {output_path}")

    # List of columns to extract
    columns_to_extract = [
        "country",
        "year",
        "iso_code",
        "population",
        "gdp",
        "biofuel_electricity",
        "carbon_intensity_elec",
        "coal_electricity",
        "electricity_demand",
        "electricity_generation",
        "fossil_electricity",
        "gas_electricity",
        "greenhouse_gas_emissions",
        "hydro_electricity",
        "low_carbon_electricity",
        "net_elec_imports_share_demand",
        "nuclear_electricity",
        "oil_electricity",
        "other_renewable_electricity",
        "other_renewable_exc_biofuel_electricity",
        "per_capita_electricity",
        "renewables_electricity",
        "solar_electricity",
        "wind_electricity"
    ]

    # Read the CSV file
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"Input file not found at: {input_path}")
        return

    # Extract the desired columns and filter for year 2022 and non-empty iso_code
    df = df[columns_to_extract]
    df = df[(df["year"] == 2022) & (df["iso_code"].notna())]

    # 1. Add "electricity_demand_generation_ratio" = electricity_demand / electricity_generation
    df["electricity_demand_generation_ratio"] = df["electricity_demand"] / df["electricity_generation"]

    # 2. Add "electricity_demand_generation_ratio_rating":
    #    - 0 if ratio == 1,
    #    - 5 if ratio > 1,
    #    - 0 if ratio < 1.
    df["electricity_demand_generation_ratio_rating"] = df["electricity_demand_generation_ratio"].apply(
        lambda x: 0 if x == 1 else (5 if x > 1 else 0)
    )

    # 3. Add "per_capita_electricity_rating":
    #    - 1 if per_capita_electricity < 1,000,000;
    #    - 2 if between 1,000,000 and 10,000,000;
    #    - 3 if above 10,000,000.
    def per_capita_rating(val):
        if val < 1_000_000:
            return 1
        elif val <= 10_000_000:
            return 2
        else:
            return 3
    df["per_capita_electricity_rating"] = df["per_capita_electricity"].apply(per_capita_rating)

    # 4. Add "nuclear_electricity_rating":
    #    - 1 if nuclear_electricity == 0;
    #    - 3 if nuclear_electricity > 0.
    df["nuclear_electricity_rating"] = df["nuclear_electricity"].apply(lambda x: 1 if x == 0 else 3)

    # 5. Add "net_elec_imports_share_demand_rating":
    #    - 0 if net_elec_imports_share_demand is >= 0;
    #    - 3 if net_elec_imports_share_demand < 0.
    df["net_elec_imports_share_demand_rating"] = df["net_elec_imports_share_demand"].apply(
        lambda x: 0 if x >= 0 else 3
    )

    # 6. Add "risk_sum": Sum of the four rating columns
    df["risk_sum"] = (
        df["per_capita_electricity_rating"] +
        df["nuclear_electricity_rating"] +
        df["net_elec_imports_share_demand_rating"] +
        df["electricity_demand_generation_ratio_rating"]
    )

    # Save the filtered data with new columns to a new CSV file
    df.to_csv(output_path, index=False)
    print(f"File successfully saved at '{output_path}' with {len(df)} rows.")

if __name__ == "__main__":
    prepare_energy_data()
