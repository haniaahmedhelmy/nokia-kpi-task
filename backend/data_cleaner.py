import pandas as pd
from pathlib import Path

def clean_and_aggregate(input_path: str, output_path: str) -> pd.DataFrame:
    """Clean raw dataset and aggregate KPI values by date."""
    
    # Load raw CSV
    df = pd.read_csv(input_path)

    # Standardize column names
    df.rename(columns={df.columns[0]: "date", df.columns[1]: "sitecode"}, inplace=True)
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

    # KPI columns = everything except date & sitecode
    kpi_cols = [col for col in df.columns if col not in ["date", "sitecode"]]

    # 1: Aggregate by date (sum KPIs across sites)
    agg_df = df.groupby("date", as_index=False)[kpi_cols].sum(min_count=1)
    # (min_count=1 → keep NaN if all values are NaN instead of replacing with 0)

    # 2: Drop rows with no KPI data at all
    agg_df = agg_df.dropna(how="all", subset=kpi_cols)

    # Save cleaned dataset
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    agg_df.to_csv(output_path, index=False)

    return agg_df

# Run directly from CLI
if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    input_file = BASE_DIR / "dataset.csv"                        # Raw input
    output_file = BASE_DIR / "backend" / "cleaned_dataset.csv"   # Cleaned output
    cleaned_agg_df = clean_and_aggregate(input_file, output_file)
    print(f"Cleaned and aggregated dataset saved to: {output_file}")
