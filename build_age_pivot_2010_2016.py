# build_age_pivot.py
import pandas as pd
import numpy as np

INPUT_TSV = "visits_with_dob_2016.tsv"   # RESORT, ARRIVAL_DATE, NAME_ID, RESV_NAME_ID, DOB
CSV_OUT   = "pivot_by_age_group_2016.csv"
XLSX_OUT  = "pivot_by_age_group_2016.xlsx"  # по избор; може да се махне
YEAR_FROM = 2007
YEAR_TO   = 2016

print("Reading TSV...")
# Ако файлът е много голям, можеш да добавиш: engine="python", on_bad_lines="skip"
df = pd.read_csv(INPUT_TSV, sep="\t", dtype=str)

# Увери се, че колоните съществуват
if "ARRIVAL_DATE" not in df.columns:
    raise RuntimeError("Missing column ARRIVAL_DATE in input file.")
if "DOB" not in df.columns:
    df["DOB"] = ""

print("Parsing ARRIVAL_DATE and extracting year/month/day...")
df["ARRIVAL_DATE"] = pd.to_datetime(df["ARRIVAL_DATE"], format="%Y-%m-%d", errors="coerce")
df = df[~df["ARRIVAL_DATE"].isna()].copy()
df["ARRIVAL_YEAR"] = df["ARRIVAL_DATE"].dt.year
df["ARRIVAL_MD"] = df["ARRIVAL_DATE"].dt.month * 100 + df["ARRIVAL_DATE"].dt.day

print("Validating DOB with regex and splitting into components...")
dob_raw = df["DOB"].fillna("").astype(str).str.strip()

# match само DD.MM.YYYY
m = dob_raw.str.extract(r"^\s*(?P<D>\d{1,2})\.(?P<M>\d{1,2})\.(?P<Y>\d{4})\s*$")
# m е DataFrame с колони D,M,Y и NaN, ако не съвпада

df["DOB_D"] = pd.to_numeric(m["D"], errors="coerce")
df["DOB_M"] = pd.to_numeric(m["M"], errors="coerce")
df["DOB_Y"] = pd.to_numeric(m["Y"], errors="coerce")

# базова валидност (не влизаме в дълбока календарна валидация)
valid = (
    df["DOB_D"].between(1, 31)
    & df["DOB_M"].between(1, 12)
    & df["DOB_Y"].between(1900, YEAR_TO)
)

print("Computing ages without datetime subtraction...")
dob_md = (df["DOB_M"] * 100 + df["DOB_D"])
before_bday = (df["ARRIVAL_MD"] < dob_md)

age_years = np.where(
    valid,
    df["ARRIVAL_YEAR"] - df["DOB_Y"] - before_bday.astype(int),
    np.nan
)
# нереалистични възрасти -> NaN
age_years = np.where((age_years >= 0) & (age_years <= 200), age_years, np.nan)
df["AGE"] = pd.to_numeric(age_years, errors="coerce")

print("Bucketing into age groups...")
labels = ["до 18", "19-26", "27-40", "41-55", "56-70", "над 70"]
bins   = [-1, 18, 26, 40, 55, 70, 200]
df["AGE_GROUP"] = pd.cut(df["AGE"], bins=bins, labels=labels)
df["AGE_GROUP"] = df["AGE_GROUP"].cat.add_categories("неизвестна възраст").fillna("неизвестна възраст")

print("Building pivot 2010..2016...")
all_years = list(range(YEAR_FROM, YEAR_TO + 1))
pivot = pd.pivot_table(
    df,
    index="AGE_GROUP",
    columns="ARRIVAL_YEAR",
    values="NAME_ID",   # всеки ред = 1 човек/посещение
    aggfunc="count",
    fill_value=0
)

row_order = ["до 18", "19-26", "27-40", "41-55", "56-70", "над 70", "неизвестна възраст"]
pivot = pivot.reindex(row_order)
pivot = pivot.reindex(columns=all_years, fill_value=0)

# Totals
pivot["Общо"] = pivot.sum(axis=1)
totals_row = pivot.sum(axis=0).to_frame().T
totals_row.index = ["Общо"]
pivot = pd.concat([pivot, totals_row], axis=0)

print(f"Writing CSV -> {CSV_OUT}")
pivot.to_csv(CSV_OUT, encoding="utf-8-sig")

try:
    print(f"Writing XLSX -> {XLSX_OUT}")
    with pd.ExcelWriter(XLSX_OUT, engine="xlsxwriter") as writer:
        pivot.to_excel(writer, sheet_name="AgePivot")
except Exception as e:
    print(f"XLSX write skipped ({e})")

print("Done.")
