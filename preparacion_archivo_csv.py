import shutil, os, zipfile
from pathlib import Path
from tkinter import filedialog
import pandas as pd



def unzipear(file):

    comercios = (1, 9, 12, 15, 16, 2000, 2002, 2005, 2007, 2011, 3001, 10, 11, 2013)
    file_path = os.path.dirname(file)  # obtiene el directorio
    file_name = Path(file).stem  # obtiene nombre archivo sin extension
    unzip_path = os.path.join(file_path, file_name)  # nuevo directorio donde extraer
    with zipfile.ZipFile(file, 'r') as zip_file:
        zip_file.extractall(unzip_path)
    # os.unlink(file)  # borra el archivo zip original
    lista = os.listdir(unzip_path)
    for index, item in enumerate(lista, start=1):
        if item.endswith(".zip"):
            item = os.path.join(unzip_path, item)
            new_unzip_path = os.path.join(unzip_path, str(index))
            with zipfile.ZipFile(item, 'r') as zip_item:
                zip_item.extractall(new_unzip_path)
            os.unlink(item)
    return unzip_path


def unir_csv(path):
    all_files = []
    for carpeta, subcarpetas, archivos in os.walk(path):
        for archivo in archivos:
            if archivo.endswith(".csv"):
                file_path = os.path.join(carpeta, archivo)
                all_files.append(file_path)

    combined_csv = pd.DataFrame()

    for i, file in enumerate(all_files):
        try:
            df = pd.read_csv(file, on_bad_lines='skip')
            combined_csv = pd.concat([combined_csv, df], ignore_index=True)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    # Drop duplicate columns (if exists) typically when headers are repeated
    combined_csv = combined_csv.loc[:, ~combined_csv.columns.duplicated()]

    # Save the combined `.csv` file
    combined_csv.to_csv(r"C:\Users\ddacunto.DGOGPP\Downloads\sepa_viernes\combinado.csv", index=False)
    print(f"Combined CSV saved to {path}")


if __name__ == "__main__":
    archivo = filedialog.askopenfilename(defaultextension="zip", filetypes=[("Zip", "*.zip")])
    ruta = unzipear(archivo)
    unir_csv(ruta)
