# Archivo de limpieza del dataset steam_games.json
from dateutil.parser import parse
import pandas as pd
import json

# steam_games.json
# Debido al formato particular del archivo optamos por recorrer el documento agregando cada objeto (registro) a una lista
lista_registros_steam_games = []
with open("Datasets/steam_games.json", encoding = "latin1") as archivo_steam_games:
    for registro in archivo_steam_games:
        lista_registros_steam_games.append(json.loads(registro))

# Luego, usamos pandas para desanidar los registros del archivo steam_games.json en un Dataframe facil de manipular
df_steam_games_procesado = pd.json_normalize(lista_registros_steam_games, max_level = 0)

# Observamos una correlación entre tres pares de columnas

# publisher - developer
#df_steam_games_procesado["publisher"].value_counts()
#df_steam_games_procesado["developer"].value_counts()
# Cantidad de datos no nulos
#df_steam_games_procesado[["publisher", "developer"]].info() # 24083 - 28836

# app_name - title
#df_steam_games_procesado["app_name"].value_counts()
#df_steam_games_procesado["title"].value_counts()
# Cantidad de datos no nulos
#df_steam_games_procesado[["app_name", "title"]].info() # 32133 - 30085

# genres - tags
#df_steam_games_procesado["genres"].value_counts()
#df_steam_games_procesado["tags"].value_counts()
# Cantidad de datos no nulos
#df_steam_games_procesado[["genres", "tags"]].info() # 28852 - 31972

# Obtenemos el año de la columna "release_date"

# Unificamos los formatos de las fechas en la columna "release_date"
date_format = "%Y-%m-%d"
def unifiqueDates(date_without_formating):
    try:
        return parse(date_without_formating).strftime(date_format)
    except:
        return None
df_steam_games_procesado["release_date"] = df_steam_games_procesado["release_date"].apply(unifiqueDates)

# Obtenemos el año a partir de la fecha formateada usando slicing
def toYear(date):
    try:
        return int(date[:4])
    except:
        return None
df_steam_games_procesado["release_date"] = df_steam_games_procesado["release_date"].apply(toYear)

# Eliminamos las columnas redundantes y que no son de interes. Borramos los registros nulos
df_steam_games_procesado.drop(columns = ["publisher", "genres", "title", "url", "reviews_url", "specs", "early_access"], inplace = True)
df_steam_games_procesado.dropna(inplace = True)

# Renombramos y Reordenamos las columnas para facilitar la interpretación
df_steam_games_procesado.rename(columns = {
    "id": "id_app",
    "release_date": "release_year",
    "tags": "genres",
}, inplace = True)
new_order = ["id_app", "app_name", "developer", "release_year", "price", "genres"]
df_steam_games_procesado = df_steam_games_procesado[new_order]

# Desanidamos los géneros presentes en la columna "genres"
df_steam_games_procesado = df_steam_games_procesado.explode(["genres"])

# Convertimos las variables categóricas de la columna "genres" a variables dummies
df_steam_games_procesado = pd.get_dummies(df_steam_games_procesado, prefix = "genre", prefix_sep = "_", columns = ["genres"], dtype = int)

# Debido a que hicimos crecer mucho el tamaño del DataFrame, agrupamos los datos por cada juego sumando las variables que convertimos a dummies
df_steam_games_procesado = df_steam_games_procesado.groupby(df_steam_games_procesado.columns.to_list()[:5])[df_steam_games_procesado.columns.to_list()[5:]].sum().reset_index()

# Convertimos las variables categóricas a numéricas en la columna "price"
def parseNumber(value):
    try:
        return float(value)
    except:
        return 0
df_steam_games_procesado["price"] = df_steam_games_procesado["price"].apply(parseNumber)

# El DataFrame ahora esta listo para guardarse en un archivo parquet para mejor redimiento
df_steam_games_procesado.to_parquet("Datasets/steam_games.parquet", engine = "pyarrow")