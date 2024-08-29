import shutil
import os
import zipfile
from pathlib import Path
from tkinter import filedialog
import pandas as pd

# Constantes
CODIGOS_COMERCIO = (3, 9, 12, 15, 16, 2000, 2002, 2005, 2007, 2011, 3001, 10, 11, 2013)


def extraer_zip_en_directorio(archivo_zip, directorio_destino):
    with zipfile.ZipFile(archivo_zip, "r") as zip_ref:
        zip_ref.extractall(directorio_destino)


def manejar_archivos_comercio(directorio_base, archivos_extraidos):
    for item in archivos_extraidos:
        ruta_item = os.path.join(directorio_base, item)
        if ruta_item.endswith(".zip"):
            for codigo in CODIGOS_COMERCIO:
                if f"comercio-sepa-{codigo}_" in item:
                    directorio_extraccion = os.path.join(directorio_base, str(codigo))
                    extraer_zip_en_directorio(ruta_item, directorio_extraccion)
            os.unlink(ruta_item)


def descomprimir_archivo(archivo):
    directorio_archivo = os.path.dirname(archivo)
    nombre_archivo = Path(archivo).stem
    directorio_extraccion = os.path.join(directorio_archivo, nombre_archivo)

    extraer_zip_en_directorio(archivo, directorio_extraccion)
    os.unlink(archivo)

    archivos_extraidos = os.listdir(directorio_extraccion)
    manejar_archivos_comercio(directorio_extraccion, archivos_extraidos)

    return directorio_extraccion


def combinar_archivos_csv(ruta, tipo_archivo, dataframe_combinado):
    for raiz, _, archivos in os.walk(ruta):
        for archivo in archivos:
            if archivo == tipo_archivo:
                try:
                    df = pd.read_csv(os.path.join(raiz, archivo), on_bad_lines="skip")
                    df = df.iloc[:-1]  # Elimina la última fila
                    dataframe_combinado = pd.concat(
                        [dataframe_combinado, df], ignore_index=True
                    )
                except Exception as e:
                    print(f"Error leyendo {archivo}: {e}")

    dataframe_combinado = dataframe_combinado.loc[
        :, ~dataframe_combinado.columns.duplicated()
    ]
    return dataframe_combinado


def combinar_y_guardar_csvs(ruta, directorio_destino):
    datos_combinados = {
        "comercios.csv": pd.DataFrame(),
        "productos.csv": pd.DataFrame(),
        "sucursales.csv": pd.DataFrame(),
    }

    for tipo_archivo, df_combinado in datos_combinados.items():
        datos_combinados[tipo_archivo] = combinar_archivos_csv(
            ruta, tipo_archivo, df_combinado
        )
        datos_combinados[tipo_archivo].to_csv(
            os.path.join(directorio_destino, tipo_archivo), index=False
        )

    for raiz, _, _ in os.walk(ruta):
        if raiz != ruta:
            try:
                shutil.rmtree(raiz)
            except Exception as e:
                print(f"Error al eliminar {raiz}: {e}")


if __name__ == "__main__":
    archivo_zip = filedialog.askopenfilename(
        defaultextension="zip", filetypes=[("Zip", "*.zip")]
    )
    ruta_extraccion = descomprimir_archivo(archivo_zip)
    directorio_salida = filedialog.askdirectory()
    combinar_y_guardar_csvs(ruta_extraccion, directorio_salida)