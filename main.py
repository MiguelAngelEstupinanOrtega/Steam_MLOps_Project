from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fastapi import FastAPI
import pandas as pd
import numpy as np

app = FastAPI()

dataset = pd.read_parquet("Datasets/steam_games.parquet").copy()

# Creamos el primer endpoint de la API
@app.get("/developerInfo/{developer}")
def developerInfo(developer : str):
    # Creamos un DataFrame con las columnas que nos interesan
    data = dataset[["id_app", "developer", "release_year", "price"]]
    
    # Aplicamos una máscara para filtrar por desarrollador
    mask = data["developer"] == developer
    data_from_developer = data[mask]
    
    # Con los datos filtrados procedemos a agruparlos por año contando la cantidad de items y hayando el porcentaje de items gratuitos
    def freeItemsPercentage(serie):
        count_free_items = (serie == 0).sum()
        count_total_items = serie.count()
        return (count_free_items / count_total_items) * 100
    
    data_from_developer_grouped_by_year = data_from_developer[["id_app", "release_year", "price"]].groupby("release_year").agg({
        "id_app": "count",
        "price": freeItemsPercentage
    }).reset_index()
    # Generamos el formato Json para la respuesta de la API
    response_dic = {}
    years_count = data_from_developer_grouped_by_year["release_year"].shape[0]
    for i in range(years_count):
        response_dic[data_from_developer_grouped_by_year["release_year"].iloc[i]] = {
            "Cantidad de items": int(data_from_developer_grouped_by_year["id_app"].iloc[i]),
            "Porcentaje de contenido gratuito": f'{(round(data_from_developer_grouped_by_year["price"].iloc[i] * 100, 0)) / 100}%'
        }
    
    return response_dic

# Realizamos ahora el modelo de recomendación

# Cargamos los datos del archivo "steam_games.parquet" en un DataFrame
data_pre = pd.read_parquet("Datasets/steam_games.parquet")
data = data_pre.sample(frac = 0.3, random_state = 1)

# Creamos la representación númerica de las columnas "app_name" y "genres" usando TfidfVectorizer
vectorizer = TfidfVectorizer()
tfidf_id_app = vectorizer.fit_transform(data["app_name"])
tfidf_genres = vectorizer.fit_transform(data["genres"])

# Apilamos las columnas que vamos a usar para el modelo de recomendación en una matriz
features_matrix = np.column_stack([tfidf_id_app.toarray(), data["release_year"], data["price"], tfidf_genres.toarray()])

# Calculamos la similitud del coseno de la matriz
similarity_matrix = cosine_similarity(features_matrix)

# Reiniciamos el indice a partir de 0 para ordenar los items
data = data.reset_index(drop = True)

# Creamos el endpoint de la API para el modelo de recomendación
@app.post("/gameRecomendation/{item_name}")
def gameRecomendation(item_name: str):
    # Creamos la máscara para obtener el item a partir de el cuál se va a hacer la recomendación
    mask = data["app_name"] == item_name
    item = data[mask]
    
    # Creamos una condición para depurar un posible error
    if not item.empty:
        # Extraemos el indice de 
        item_index = item.index[0]
        
        # Usamos el indice para encontrar items similares
        item_similarities = similarity_matrix[item_index]
        
        # Ordenamos los items recomendados de acuerdo a su similitud con el juego dado y seleccionamos los 5 primeros sin contar el juego a partir del cual hacemos la recomendación
        most_similar_item_indices = np.argsort(-item_similarities)
        most_similar_items = data.loc[most_similar_item_indices, "app_name"][1:6]
        
        # Devolvemos el resultado en el formato requerido
        response_dic = {}
        for i in range(5):
            response_dic[i + 1] = most_similar_items.iloc[i]
        return response_dic
    else:
        return "Item no existente. Verifique la sintaxis"