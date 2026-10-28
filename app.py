"""Servicio web (FastAPI) para el modelo de precios de casas en California.

Modelo: regresión lineal entrenada en la Práctica 1 con housing.csv
(modelo_california.pkl). Predice median_house_value (en dólares).
Autores: Samuel Rodriguez y Alejandro Rauseo

Ejecución en local (con modelo_california.pkl en la misma carpeta):
    uvicorn app:app --reload
Comando de arranque en Render (Start Command):
    uvicorn app:app --host 0.0.0.0 --port $PORT
"""
import os
from contextlib import asynccontextmanager
from typing import Literal

import joblib
import pandas as pd
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

MODEL_PATH = "modelo_california.pkl"
# URL "raw" del modelo en nuestro repositorio de GitHub (ejercicio 8)
MODEL_URL = "https://raw.githubusercontent.com/samuelrdgzm/prediccion-casas-california/main/modelo_california.pkl"
DOWNLOAD_TIMEOUT = 30  # segundos

# El modelo se carga al arrancar y se guarda aquí.
state = {"model": None}

OCEAN_VALUES = ["<1H OCEAN", "INLAND", "ISLAND", "NEAR BAY", "NEAR OCEAN"]


class HouseFeatures(BaseModel):
    """Variables de entrada del modelo (una zona censal de housing.csv)."""
    longitude: float
    latitude: float
    housing_median_age: float
    total_rooms: float
    total_bedrooms: float
    population: float
    households: float
    median_income: float
    ocean_proximity: Literal["<1H OCEAN", "INLAND", "ISLAND", "NEAR BAY", "NEAR OCEAN"]


def download_model(url: str = MODEL_URL, path: str = MODEL_PATH):
    """Descarga el modelo desde `url` (GitHub) y lo guarda en `path`."""
    response = requests.get(url, timeout=DOWNLOAD_TIMEOUT)
    response.raise_for_status()
    with open(path, "wb") as f:
        f.write(response.content)
    print(f"Modelo descargado de {url} y guardado en {path}")


def load_model(path: str = MODEL_PATH):
    """Carga el modelo. Si no existe en local, lo descarga antes de GitHub."""
    if not os.path.exists(path):
        print(f"{path} no encontrado en local, descargando...")
        download_model()
    return joblib.load(path)


def build_dataframe(features: HouseFeatures, columns) -> pd.DataFrame:
    """Convierte la entrada en las 13 columnas que espera el modelo.

    ocean_proximity se transforma en 5 columnas 0/1 (one-hot), como en el
    entrenamiento (pd.get_dummies).
    """
    data = features.model_dump()
    ocean = data.pop("ocean_proximity")
    for value in OCEAN_VALUES:
        data[f"ocean_proximity_{value}"] = 1.0 if ocean == value else 0.0
    return pd.DataFrame([data])[list(columns)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Se ejecuta una vez al arrancar el servicio."""
    state["model"] = load_model()
    yield


app = FastAPI(title="Precio de casas en California", lifespan=lifespan)


@app.get("/")
def health():
    """Health-check: confirma que el servicio está funcionando."""
    return {"status": "ok"}


@app.post("/predict")
def predict(features: HouseFeatures):
    """Devuelve el precio medio estimado de la vivienda (en dólares)."""
    model = state["model"]
    if model is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado")
    X = build_dataframe(features, model.feature_names_in_)
    prediction = model.predict(X)[0]
    return {"median_house_value": float(prediction)}
