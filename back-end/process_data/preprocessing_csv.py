# %% filer and delete null columns
import csv
from pathlib import Path
import pandas as pd

data_path = Path("database_csv")
# %% fix csv file
"""
Because raw data has error files('broken_files' defined below,)
which specific error columns. The error is column contain sign ','.
So csv reader understand that it is 1 column and we mismatch with header column.

WARNING: ONLY RUN THE CODE BELOW IN FIRST TIME!
Then copy fixed files to origin folder (Remember that delete error files).
"""
fixed_path = Path("database_csv_fixed")
fixed_path.mkdir(exist_ok=True)

broken_files = {
    'customers.csv': 'address',
    'orders.csv': 'shipAddress',
    'suppliers.csv': 'address'
}

def fix_csv(src: Path, dst: Path, broken_col: str):
    with open(src, newline="", encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        n_cols = len(header)
        idx = header.index(broken_col)

        rows = []
        for row in reader:
            extra = len(row) - n_cols
            if extra > 0:
                merged = ",".join(row[idx: idx + extra + 1])
                row = row[:idx] + [merged] + row[idx + extra + 1:]
            rows.append(row)

    with open(dst, "w", newline="", encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        writer.writerows(rows)

for name, col in broken_files.items():
    fix_csv(data_path / name, fixed_path / name, col)
    df = pd.read_csv(fixed_path / name)
    print(name, df.shape)


# %% Checking null columns
for file_path in data_path.glob("*.csv"):
    print(f"===== Checking file {file_path.name} =====")

    try:
        df = pd.read_csv(file_path)
        null_count = df.isnull().sum()
        columns_with_null = null_count[null_count>0]
        if not columns_with_null.empty:
            print("Columns with null value:")
            for col, count in columns_with_null.items():
                print(f"- Column: '{col}': {count} null values")
        else:
            print("No columns with null value!")
    except Exception as e:
        print(f"Error when reading file {file_path.name}: {e}")
    print()

# Survey files have null columns (name column and number of null value)
# Relized that these columns can be deleted,
# except 'shippedDate' because Null value can understand this order was cancel.
null_files = [
    {
        "file_name": "customers.csv",
        "column_null": {
            "region": 60, 
            "postalCode": 1,
            "fax": 22
        }
    },
    {
        "file_name": "employees.csv",
        "column_null": {
            "region": 4, 
            "reportsTo": 1
        }
    },
    {
        "file_name": "orders.csv",
        "column_null": {
            "shippedDate": 21, 
            "shipRegion": 507,
            "shipPostalCode": 19
        }
    },
    {
        "file_name": "suppliers.csv",
        "column_null": {
            "region": 20, 
            "fax": 16,
            "homePage": 24
        }
    },
]

# %% Delete null value column
output_path = Path("database_csv_cleaned")
output_path.mkdir(parents=True, exist_ok=True)

for file_path in data_path.glob("*.csv"):
  print(f"=== Processing file: {file_path.name} ===")

  try:
    df = pd.read_csv(file_path)

    null_counts = df.isnull().sum()
    cols_to_drop = null_counts[null_counts > 0].index.tolist()

    if file_path.name == "orders.csv" and "shippedDate" in cols_to_drop:
      cols_to_drop.remove("shippedDate")

    if cols_to_drop:
      df = df.drop(columns=cols_to_drop)
      print(f"Dropped null column: {cols_to_drop}")
    else:
      print("No column dropped.")

    destination_file = output_path / file_path.name
    df.to_csv(destination_file, index=False)
    print(f"Saved in: {destination_file}")

  except Exception as e:
    print(f"Error when processing file {file_path.name}: {e}")

  print()
# %%
