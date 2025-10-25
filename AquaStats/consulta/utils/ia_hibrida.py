# consulta/utils/ia_hibrida.py
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from django.conf import settings

MODEL_PATH = os.path.join(settings.BASE_DIR, 'modelo_ia_hibrido.pkl')

def entrenar_modelo(df):
    """
    Entrena el modelo de IA con los datos históricos y lo guarda en disco.
    """
    if df.empty:
        return None, None, None

    df['mes_num'] = df['Fecha'].dt.month
    df_mes = df.groupby('mes_num', as_index=False)['Cantidad'].mean()

    X = df_mes[['mes_num']]
    y = df_mes['Cantidad']

    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X, y)

    y_pred = modelo.predict(X)
    mse = mean_squared_error(y, y_pred)
    r2 = r2_score(y, y_pred)

    # Guardar el modelo
    joblib.dump(modelo, MODEL_PATH)
    return modelo, mse, r2

def predecir_consumo(mes, modelo=None):
    """
    Predice el consumo futuro usando el modelo entrenado.
    """
    if modelo is None and os.path.exists(MODEL_PATH):
        modelo = joblib.load(MODEL_PATH)
    if modelo is None:
        return None

    prediccion = modelo.predict(np.array([[mes]]))[0]
    return prediccion
