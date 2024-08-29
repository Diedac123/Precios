import shutil
import os
import zipfile
from pathlib import Path
from tkinter import filedialog
import pandas as pd

# Constants
COMERCIO_CODES = (3, 9, 12, 15, 16, 2000, 2002, 2005, 2007, 2011, 3001, 10, 11, 2013)


def extract_zip_to_dir(zip_file, extract_to):
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(extract_to)


def handle_comercio_zips(base_path, extracted_files):
    for item in extracted_files:
        item_path = os.path.join(base_path, item)
        if item_path.endswith(".zip"):
            for code in COMERCIO_CODES:
                if f"comercio-sepa-{code}_" in item:
                    extract_to = os.path.join(base_path, str(code))
                    extract_zip_to_dir(item_path, extract_to)
            os.unlink(item_path)


def unzip_file(file):
    file_dir = os.path.dirname(file)
    file_name = Path(file).stem
    extract_to = os.path.join(file_dir, file_name)

    extract_zip_to_dir(file, extract_to)
    os.unlink(file)

    extracted_files = os.listdir(extract_to)
    handle_comercio_zips(extract_to, extracted_files)

    return extract_to


def combine_csv_files(path, file_type, combined_df):
    for root, _, files in os.walk(path):
        for file in files:
            if file == file_type:
                try:
                    df = pd.read_csv(os.path.join(root, file), on_bad_lines="skip")
                    df = df.iloc[:-1]  # Remove last row
                    combined_df = pd.concat([combined_df, df], ignore_index=True)
                except Exception as e:
                    print(f"Error reading {file}: {e}")

    combined_df = combined_df.loc[:, ~combined_df.columns.duplicated()]
    return combined_df


def combine_and_save_csvs(path, output_dir):
    combined_data = {
        "comercios.csv": pd.DataFrame(),
        "productos.csv": pd.DataFrame(),
        "sucursales.csv": pd.DataFrame(),
    }

    for file_type, combined_df in combined_data.items():
        combined_data[file_type] = combine_csv_files(path, file_type, combined_df)
        combined_data[file_type].to_csv(
            os.path.join(output_dir, file_type), index=False
        )

    for root, _, _ in os.walk(path):
        if root != path:
            try:
                shutil.rmtree(root)
            except Exception as e:
                print(f"Error deleting {root}: {e}")


if __name__ == "__main__":
    zip_file = filedialog.askopenfilename(
        defaultextension="zip", filetypes=[("Zip", "*.zip")]
    )
    extraction_path = unzip_file(zip_file)
    output_directory = filedialog.askdirectory()
    combine_and_save_csvs(extraction_path, output_directory)