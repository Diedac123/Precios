import shutil, os, zipfile
from pathlib import Path
from tkinter import filedialog
import pandas as pd


def unzipear(file):

    comercios = (3, 9, 12, 15, 16, 2000, 2002, 2005, 2007, 2011, 3001, 10, 11, 2013)
    file_path = os.path.dirname(file)  # obtiene el directorio
    file_name = Path(file).stem  # obtiene nombre archivo sin extension
    unzip_path = os.path.join(file_path, file_name)  # nuevo directorio donde extraer
    with zipfile.ZipFile(file, "r") as zip_file:
        zip_file.extractall(unzip_path)
    os.unlink(file)  # borra el archivo zip original
    lista = os.listdir(unzip_path)
    for item in lista:
        item = os.path.join(unzip_path, item)
        if item.endswith(".zip"):
            for comercio in comercios:
                if f"comercio-sepa-{comercio}_" in item:
                    new_unzip_path = os.path.join(unzip_path, str(comercio))
                    with zipfile.ZipFile(item, "r") as zip_item:
                        zip_item.extractall(new_unzip_path)
        os.unlink(item)
    return unzip_path


def unir_csv(path):
    carpetas_a_borrar = []
    archivos_comercios = []
    archivos_productos = []
    archivos_sucursales = []
    for carpeta, subcarpetas, archivos in os.walk(path):
        carpetas_a_borrar.append(carpeta)
        for archivo in archivos:
            if archivo == "comercio.csv":
                file_path = os.path.join(carpeta, archivo)
                archivos_comercios.append(file_path)
            elif archivo == "productos.csv":
                file_path = os.path.join(carpeta, archivo)
                archivos_productos.append(file_path)
            elif archivo == "sucursales.csv":
                file_path = os.path.join(carpeta, archivo)
                archivos_sucursales.append(file_path)

    directorio = filedialog.askdirectory()

    combinado_comercios = pd.DataFrame()
    combinado_productos = pd.DataFrame()
    combinado_sucursales = pd.DataFrame()

    cvs_a_combinar = [combinado_comercios, combinado_productos, combinado_sucursales]
    archivos_a_combinar = [archivos_comercios, archivos_productos, archivos_sucursales]
    nombres_archivos = ["comercios", "productos", "sucursales"]

    for i in range(len(cvs_a_combinar)):
        for file in archivos_a_combinar[i]:
            try:
                df = pd.read_csv(file, on_bad_lines="skip")
                df = df.iloc[:-1]  # elimina la ultima fila
                cvs_a_combinar[i] = pd.concat(
                    [cvs_a_combinar[i], df], ignore_index=True
                )
            except Exception as e:
                print(f"Error reading {file}: {e}")

        # Drop duplicate columns (if exists) typically when headers are repeated
        cvs_a_combinar[i] = cvs_a_combinar[i].loc[
            :, ~cvs_a_combinar[i].columns.duplicated()
        ]

        # Save the combined `.csv` file
        cvs_a_combinar[i].to_csv(
            f"{directorio}/{nombres_archivos[i]}.csv",
            index=False,
        )

    for carpeta in carpetas_a_borrar[1:]:
        try:
            shutil.rmtree(carpeta)
        except Exception as e:
            print(f"Error al eliminar el directorio {carpeta}: {e}")


if __name__ == "__main__":
    archivo = filedialog.askopenfilename(
        defaultextension="zip", filetypes=[("Zip", "*.zip")]
    )
    ruta = unzipear(archivo)
    unir_csv(ruta)
