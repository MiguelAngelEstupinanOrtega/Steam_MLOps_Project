from fastapi import FastAPI
import pandas as pd

app = FastAPI()

dataset = pd.read_parquet("Datasets/steam_games.parquet").copy()

@app.get("/")
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