import pandas as pd
from pathlib import Path

def clean_and_aggregate(input_path: str, output_path: str) -> pd.DataFrame:
    df = pd.read_csv(input_path)

    df.rename(columns={df.columns[0]: "date", df.columns[1]: "sitecode"}, inplace=True)
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

    kpi_cols = [col for col in df.columns if col not in ["date", "sitecode"]]
    df = df.dropna(how="all", subset=kpi_cols)
    df["week"] = df["date"].dt.to_period("W")

    global_mins = df[kpi_cols].min(skipna=True)

    for week, group in df.groupby("week"):
        for kpi in kpi_cols:
            week_values = group[kpi].dropna()
            if week_values.empty:
                df.loc[df["week"] == week, kpi] = global_mins[kpi]
            else:
                week_min = week_values.min()
                df.loc[(df["week"] == week) & (df[kpi].isna()), kpi] = week_min

    df = df.drop(columns=["week"])
    agg_df = df.groupby("date", as_index=False)[kpi_cols].sum()

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    agg_df.to_csv(output_path, index=False)
    return agg_df


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    input_file = BASE_DIR / "dataset.csv"
    output_file = BASE_DIR / "backend" / "cleaned_dataset.csv"
    cleaned_agg_df = clean_and_aggregate(input_file, output_file)
    print(f"Cleaned and aggregated dataset saved to: {output_file}")
