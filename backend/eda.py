import pandas as pd

# Load dataset (use engine="pyxlsb" if file is .xlsb)
df = pd.read_excel("dataset (version 1).xlsb", engine="pyxlsb")

# -------------------------
# 1. Missing values per KPI
# -------------------------
kpi_columns = [col for col in df.columns if col.startswith("kpi")]
missing_per_kpi = df[kpi_columns].isnull().sum()

print("📊 Missing values per KPI:")
print(missing_per_kpi)
print()

# -------------------------
# 2. Total rows in dataset
# -------------------------
total_rows = len(df)
print(f"Total rows in dataset: {total_rows}")
print()

# -------------------------
# 3. Rows after dropping empty sites
# -------------------------
# Find sites where ALL KPIs are missing
site_missing = df.groupby("sitecode")[kpi_columns].apply(
    lambda x: x.isnull().all().all()
)

empty_sites = site_missing[site_missing].index.tolist()
print(f"Empty Sites: {empty_sites}")
print(f"Number of empty sites: {len(empty_sites)}")
print()

# Drop those sites
df_cleaned = df[~df["sitecode"].isin(empty_sites)]
remaining_rows = len(df_cleaned)

print(f"Remaining rows after dropping empty sites: {remaining_rows}")
site_missing = df.groupby("sitecode")[kpi_columns].apply(
    lambda x: x.isnull().all().all()
)
empty_sites = site_missing[site_missing].index.tolist()

print("🟥 Completely Empty Sites:")
print(empty_sites)
print(f"Total completely empty sites: {len(empty_sites)}")
print()

# -------------------------
# 2. Partially empty sites
# -------------------------
# A row is "empty" if all KPIs are NaN
df["all_kpis_missing"] = df[kpi_columns].isnull().all(axis=1)

# Sites that have both True (all missing) and False (some data)
site_status = df.groupby("sitecode")["all_kpis_missing"].agg(["any", "all"])
partial_sites = site_status[(site_status["any"]) & (~site_status["all"])].index.tolist()

print("🟨 Partially Empty Sites:")
print(partial_sites)
print(f"Total partially empty sites: {len(partial_sites)}")
print()

# -------------------------
# 3. Empty dates for each partially empty site
# -------------------------
empty_dates_per_site = (
    df[df["all_kpis_missing"]]
    .groupby("sitecode")["PERIOD_START_TIME"]
    .apply(list)
    .to_dict()
)

print("📅 Empty Dates per Partially Empty Site:")
for site, dates in empty_dates_per_site.items():
    print(f"{site}: {dates[:10]}{'...' if len(dates) > 10 else ''}")  # only preview 10 dates
print()

# Keep only Site + KPI columns (assuming your KPIs are named like kpi001 ... kpi009)
kpi_cols = [col for col in df.columns if col.startswith("kpi") and col[:6] in ["kpi001","kpi002","kpi003","kpi004","kpi005","kpi006","kpi007","kpi008","kpi009"]]

# Group by Site and calculate min and max for each KPI
site_kpi_stats = df.groupby("sitecode")[kpi_cols].agg(["min", "max"])

# Flatten multi-level columns (so it's easier to read)
site_kpi_stats.columns = [f"{kpi}_{stat}" for kpi, stat in site_kpi_stats.columns]

# Reset index so Site becomes a column again
site_kpi_stats = site_kpi_stats.reset_index()
# Export to Excel
site_kpi_stats.to_excel("site_kpi_min_max.xlsx", index=False)
# Display nicely
print(site_kpi_stats.head())

# Identify KPI columns (assuming they are named kpi1, kpi2, ..., kpi9)
kpi_cols = [col for col in df.columns if col.lower().startswith("kpi")]

# Drop rows where ALL KPIs are missing
cleaned_df = df.dropna(subset=kpi_cols, how="all")

# Save to a new Excel file
cleaned_df.to_excel("cleaned_dataset.xlsx", index=False)

print(f"Original dataset rows: {len(df)}")
print(f"Cleaned dataset rows: {len(cleaned_df)}")
print("✅ Cleaned dataset saved as cleaned_dataset.xlsx")

#################################################################
import pandas as pd

# Read CSV
df = pd.read_csv("dataset.csv")

# Identify KPI columns
kpi_columns = [col for col in df.columns if col.lower().startswith("kpi")]

# Drop rows where all KPIs are missing
df_cleaned = df.dropna(how="all", subset=kpi_columns)

# Save back to CSV (date column will remain exactly as in original)
df_cleaned.to_csv("dataset_cleaned.csv", index=False)
