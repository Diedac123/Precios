import shutil
import os
import zipfile
from pathlib import Path
from tkinter import filedialog
import pandas as pd

# Constantes
CODIGOS_COMERCIO = (3, 9, 12, 15, 16, 2000, 2002, 2005, 2007, 2011, 3001, 10, 11, 2013)


def extraer_zip_en_directorio(archivo_zip, directorio_destino):
    """

    La función `extraer_zip_en_directorio` toma como entrada un archivo zip y un directorio de destino, y extrae el contenido del archivo zip en el directorio especificado.

    :param archivo_zip: Ruta del archivo zip que se desea extraer.
    :param directorio_destino: Ruta del directorio en el que se extraerá el contenido del archivo zip.

    :return: None
    """
    with zipfile.ZipFile(archivo_zip, "r") as zip_ref:
        zip_ref.extractall(directorio_destino)


def manejar_archivos_comercio(directorio_base, archivos_extraidos):
    """

    Esta función se encarga de manejar archivos comercio. Recibe dos parámetros: directorio_base y archivos_extraidos.

    :param directorio_base: El directorio base donde se encuentran los archivos.
    :param archivos_extraidos: Una lista de nombres de archivos que se han extraído.

    :return: No devuelve ningún valor.

    """
    for item in archivos_extraidos:
        ruta_item = os.path.join(directorio_base, item)
        if ruta_item.endswith(".zip"):
            for codigo in CODIGOS_COMERCIO:
                if f"comercio-sepa-{codigo}_" in item:
                    directorio_extraccion = os.path.join(directorio_base, str(codigo))
                    extraer_zip_en_directorio(ruta_item, directorio_extraccion)
            os.unlink(ruta_item)


def descomprimir_archivo(archivo):
    """
    Descomprime un archivo y realiza ciertas operaciones con los archivos extraídos.

    :param archivo: La ruta del archivo que se desea descomprimir.
    :return: La ruta del directorio donde se extrajeron los archivos.
    """
    directorio_archivo = os.path.dirname(archivo)
    nombre_archivo = Path(archivo).stem
    directorio_extraccion = os.path.join(directorio_archivo, nombre_archivo)

    extraer_zip_en_directorio(archivo, directorio_extraccion)
    os.unlink(archivo)

    archivos_extraidos = os.listdir(directorio_extraccion)
    manejar_archivos_comercio(directorio_extraccion, archivos_extraidos)

    return directorio_extraccion


def combinar_archivos_csv(ruta, tipo_archivo, dataframe_combinado):
    """
    Función para combinar archivos CSV en un solo DataFrame.

    :param ruta: La ruta del directorio donde se encuentran los archivos CSV.
    :param tipo_archivo: El nombre del archivo CSV que se desea combinar.
    :param dataframe_combinado: El DataFrame en el cual se van a combinar los archivos CSV.
    :return: El DataFrame combinado con los datos de todos los archivos CSV.

    La función `combinar_archivos_csv` toma la ruta de un directorio, el nombre de un archivo CSV y un DataFrame ya existente. Recorre todos los archivos en la ruta especificada y si encuentra un archivo con el nombre especificado, lo lee usando la biblioteca `pandas`. Luego, se realiza la siguiente operación en el DataFrame combinado:

    1. Se elimina la última fila del DataFrame leído.
    2. Se concatena el DataFrame leído con el DataFrame combinado, ignorando los índices existentes.
    3. Si ocurre algún error durante la lectura del archivo, se imprime un mensaje de error en la consola.

    Después de combinar todos los archivos CSV, se elimina cualquier columna duplicada en el DataFrame combinado y se devuelve el DataFrame resultante.

    Note: Este código está escrito en Python utilizando la sintaxis reStructuredText para documentar.
    """
    for raiz, _, archivos in os.walk(ruta):
        for archivo in archivos:
            if archivo == tipo_archivo:
                try:
                    df = pd.read_csv(
                        os.path.join(Path(raiz), archivo), on_bad_lines="skip"
                    )
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
    """
    La función `combinar_y_guardar_csvs` recibe dos parámetros: `ruta` y `directorio_destino`. Esta función combina y guarda archivos csv en un directorio de destino.

    :param ruta: La ruta del directorio que contiene los archivos csv a combinar.
    :param directorio_destino: El directorio de destino donde se guardarán los archivos csv combinados.
    :return: No retorna ningún valor.

    Algoritmo:
    1. Se crea un diccionario llamado `datos_combinados` con tres elementos: `comercio.csv`, `productos.csv` y `sucursales.csv`, inicializados con un DataFrame vacío de pandas.
    2. Se itera sobre el diccionario `datos_combinados` y se combinan los archivos csv en la ruta indicada utilizando la función `combinar_archivos_csv`. El resultado de la combinación se guarda en el DataFrame correspondiente en el diccionario.
    3. Se guarda cada DataFrame combinado en un archivo csv en el directorio de destino utilizando la función `to_csv` de pandas.
    4. Se realiza un recorrido del directorio `ruta` utilizando la función `os.walk`. Si la raíz actual no es igual a la ruta principal, se intenta eliminar el directorio utilizando la función `shutil.rmtree`. Si ocurre algún error durante la eliminación, se muestra un mensaje de error.

    Es importante tener en cuenta que esta función no retorna ningún valor y puede imprimir mensajes de error en caso de que ocurra un problema durante la eliminación de directorios.
    """
    datos_combinados = {
        "comercio.csv": pd.DataFrame(),
        "productos.csv": pd.DataFrame(),
        "sucursales.csv": pd.DataFrame(),
    }

    for tipo_archivo, df_combinado in datos_combinados.items():
        datos_combinados[tipo_archivo] = combinar_archivos_csv(
            ruta, tipo_archivo, df_combinado
        )
        datos_combinados[tipo_archivo].to_csv(
            os.path.join(Path(directorio_destino), tipo_archivo), index=False
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
