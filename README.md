   # Predicción del precio de casas en California (API en Render)

API REST con FastAPI que predice el valor medio de la vivienda (`median_house_value`) con la regresión lineal entrenada en la Práctica 1. Autores: Samuel Rodriguez y Alejandro Rauseo.

## Pasos seguidos para el despliegue
1. **Cuentas:** creadas en github.com y en render.com (con "Sign in with GitHub").
2. **Repositorio público** `samuelrdgzm/prediccion-casas-california` con `app.py`, `requirements.txt`, `modelo_california.pkl`, el script que genera el modelo y `medir_tiempos.py`.
3. **Servicio en Render:** New + → Web Service → repositorio, rama `main`, región Frankfurt, plan Free.
4. **Build Command:** `pip install -r requirements.txt`
5. **Start Command (comando de despliegue):** `uvicorn app:app --host 0.0.0.0 --port $PORT`
6. Tras cada cambio en GitHub: Manual Deploy → Deploy latest commit.

## URL final
https://prediccion-casas-california.onrender.com (health-check en `GET /`, predicciones en `POST /predict`, documentación en `/docs`).

## Notas
- El plan gratuito suspende el servicio tras 15 min sin tráfico: la primera petición puede tardar cerca de un minuto.
- Si `modelo_california.pkl` no está en local al arrancar, `app.py` lo descarga desde este repositorio de GitHub.
