# Steam_MLOps_Project
## Proceso de ETL

Aqui observamos que los datasets con los datos brutos (sin tratamiento) tienen un tamaño muy grande, por ende procederemos a explorar los datos para eliminar las columnas que no son de interés, los datos nulos y guardar los datasets reducidos en un archivo en formato parquet para optimizar así las busquedas de los registros.

---
## Análisis Exploratorio de Datos (EDA)
### steam_games.json

En este dataset vemos inicialmente 13 columnas, las cuales son:
- publisher
- genres
- app_name
- title
- url
- release_date
- tags
- reviews_url
- specs
- price
- early_access
- id
- developer

El análisis de estas nos dice lo siguiente:

1. Observamos que las parejas de columnas: **publisher**/**developer**, **app_name**/**title** y **genres**/**tags** tienen una correlación de datos muy alta. Es decir, los pares de columnas aportan la misma información a el proyecto, por ende, procedemos a conservar las columnas con mayor cantidad de valores **no** nulos (**developer**, **app_name**, **tags**).

2. Consideramos que las columnas: **url**, **reviews_url**, **specs** y **early_access** no aportan información de valor para los endpoints de la API, debido a ello se procede a eliminar estas columnas junto a las columnas redundantes del primer literal. Además, aplicamos el método dropna para reducir considerablemente el tamaño del dataset.

3. Debido a que la columna **release_date** contiene fechas, y solo necesitamos el año asociado a estas, aplicamos un algoritmo sobre la columna para obtener esta información.

4. Renombramos la columna **tags** como **genres** ya que esta nomenclatura nos facilitará las cosas más adelante. Además, reordenamos las columnas para facilitar su interpretación.