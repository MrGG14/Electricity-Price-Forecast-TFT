import os
import pandas as pd

from config.config_file import DATE_INFO, FASE1_SETTINGS
from config.metadata import TOKEN, PATHS
from utils.logger_utils import logger as logger1
from preprocessing.update_data_model_FI import update_data_model
from modelling.helper_mod_01.helper_model_selection import predict_spot_price
from validation.helper_metrics import update_preds_history
from datetime import datetime, timedelta

import pickle
import matplotlib.pyplot as plt
import csv

import numpy as np
import sys

basepath = os.path.dirname(__file__)
sys.path.insert(1, os.path.join(basepath))
sys.path.insert(1, os.path.join(basepath, "..\\"))
sys.path.insert(1, os.path.join(basepath, "..\\..\\validation"))

from utils.utils_model import split_train_val_test
from utils.utils_file import (
    select_data_length,
    clean_TS,
    apply_feature_engineering,
    get_dataset_input_v1,
    tope_gas_transform,
)

from config.metadata import FASE1_DATASET, PATHS, DIR
from config.config_file import FASE1_MODELS, FASE1_SETTINGS, DATE_INFO
from utils.logger_utils import logger as logger1

from validation.helper_metrics import get_error_diario

from modelling.MOD_01_ARIMA_SELECTION_AUTO import data_prep

import warnings
from datetime import datetime, timedelta

warnings.filterwarnings(action="ignore", category=UserWarning)

PATH_MODEL = os.path.join(
    PATHS["LOCAL"]["root"], "02 Ejecución/4_Modelado/Fase1"
)


yesterday = datetime.now() - timedelta(days=1)
yesterday = yesterday.strftime("%Y%m%d")

PATH_DATA = os.path.join(PATHS["LOCAL"]["root"], PATHS["LOCAL"]["src_fase1"])
FILE_DATA = os.path.join(
    PATH_DATA, "backup", f"{yesterday}_dataset_input_v0.xlsx"
)

# df = pd.read_excel(FILE_DATA)
FILE_DATA = os.path.join(PATHS['LOCAL']['root'], 'datasets', 'dataset_input_v0_2.xlsx')
new_input = update_data_model(
    date=DATE_INFO["date"],
    today_hour=DATE_INFO["update_hour"],
    path=FILE_DATA,
    download_path=PATHS["LOCAL"]["download_path"],
    token=TOKEN,
)

new_input.to_excel(FILE_DATA, index=False)

date = DATE_INFO["start_date_fase1"] + " 23:00:00"

data = new_input
data = data[
    (data[FASE1_DATASET["columns_input_v0"]["col_date"]] <= date)
].copy()

# A continuacion se va a realizar un proceso de concatenacion en varias variables.
# Se explica para la variable demanda.
# En el momento de la prediccion se utilizan ciertos datos de demanda:
# 1. la demanda real: constituida por un historico de datos de demanda, esto es, la demanda definitiva una vez ha pasado el dia
# 2. La prevision de demanda que se da para las X horas siguientes
# En el momento de hacer la prediccion para el dia siguiente no se contara con la demanda real sino con la estimacion.
# De esta forma, si se quiere dar una prediccion realista, se tendra que concatenar la serie de demanda real con la prevista y utilizar las dos informaciones

# Para hacer esta concatenacion se definen varias fechas, estas fechas mas adelante se utilizaran como limites de diferentes tramos:
# Se define la variable end_actual_0, cuyo valor son dos dias anteriores a la fecha date
end_actual_0 = str(
    datetime.strptime(date, "%Y-%m-%d %H:%M:%S") - timedelta(days=2)
)

# Se define la variable end_actual_date, cuyo valor son 1 dia anterior a la fecha date
end_actual_date = str(
    datetime.strptime(date, "%Y-%m-%d %H:%M:%S") - timedelta(days=1)
)

# Se define la variable prev_12_date, cuyo valor son 13 horas antes de la fecha date
prev_12_date = str(
    datetime.strptime(end_actual_date, "%Y-%m-%d %H:%M:%S")
    - timedelta(hours=13)
)

# A continuacion, se definen una serie de listas con los nombres de las columnas que se usaran para los diferentes tramos
real_columns = [
    FASE1_DATASET["columns_input_v0"]["col_date"],
    FASE1_DATASET["columns_input_v0"]["col_target"],
    FASE1_DATASET["columns_input_v0"]["col_demand"],
    FASE1_DATASET["columns_input_v0"]["col_co2"],
    FASE1_DATASET["columns_input_v0"]["col_gas"],
    FASE1_DATASET["columns_input_v0"]["col_eolic"],
    FASE1_DATASET["columns_input_v0"]["col_solar"],
    FASE1_DATASET["columns_input_v0"]["col_demanda_residual"],
]

pred_0 = [
    FASE1_DATASET["columns_input_v0"]["col_date"],
    FASE1_DATASET["columns_input_v0"]["col_target"],
    FASE1_DATASET["columns_input_v0"]["col_demand"],
    FASE1_DATASET["columns_input_v0"]["col_co2_prev24"],
    FASE1_DATASET["columns_input_v0"]["col_gas_prev24"],
    FASE1_DATASET["columns_input_v0"]["col_eolic"],
    FASE1_DATASET["columns_input_v0"]["col_solar"],
    FASE1_DATASET["columns_input_v0"]["col_demanda_residual"],
]
pred_1 = [
    FASE1_DATASET["columns_input_v0"]["col_date"],
    FASE1_DATASET["columns_input_v0"]["col_target"],
    FASE1_DATASET["columns_input_v0"]["col_demand_prev12"],
    FASE1_DATASET["columns_input_v0"]["col_co2_prev24"],
    FASE1_DATASET["columns_input_v0"]["col_gas_prev24"],
    FASE1_DATASET["columns_input_v0"]["col_eolic_prev12"],
    FASE1_DATASET["columns_input_v0"]["col_solar_prev12"],
    FASE1_DATASET["columns_input_v0"]["col_demanda_residual"],
]
pred_2 = [
    FASE1_DATASET["columns_input_v0"]["col_date"],
    FASE1_DATASET["columns_input_v0"]["col_target"],
    FASE1_DATASET["columns_input_v0"]["col_demand_prev36"],
    FASE1_DATASET["columns_input_v0"]["col_co2_prev48"],
    FASE1_DATASET["columns_input_v0"]["col_gas_prev48"],
    FASE1_DATASET["columns_input_v0"]["col_eolic_prev36"],
    FASE1_DATASET["columns_input_v0"]["col_solar_prev36"],
    FASE1_DATASET["columns_input_v0"]["col_demanda_residual"],
]

# La logica a seguir para realizar la concatenacion es la siguiente:
# Una vez definido date, y los tramos,  miramos que informacion vamos a incluir para cada tramo
# Para el tramo mas lejano al momento actual se utilizara solo informacion pasada historica
# Si por el contrario estamos en un tramo mas cercano a la fecha date se utilizaran previsiones.
# Esto se hace para mantener la maxima realidad posible dentro de las predicciones. Al hacer simulaciones se podrian coger simplemente datos pasados
# historicos, sin embargo, esto no representaria la realidad del dia a dia de la prediccion y podria llevar a resultados erroneos
# A continuacion se definen los diferentes tramos y los valores que se van asignando en cada uno de ellos

# Se define el dataset real_data_0 donde se utilizan las columnas de pred0 cuyas fechas estan entre end_actual_0 y prev_12_date,
# es decir, estan entre dos dias antes y 12 h antes del dia que se quiere predecir
real_data_0 = data.loc[
    (data[FASE1_DATASET["columns_input_v0"]["col_date"]] > end_actual_0)
    & (data[FASE1_DATASET["columns_input_v0"]["col_date"]] <= prev_12_date),
    pred_0,
]

# En el caso de que exista una columna entera vacia (no existe prevision en este tramo), se rellena con la informacion historica real
for i, j in zip(pred_0[1:], real_columns[1:]):
    if real_data_0[i].sum() == 0:
        real_data_0[i] = data.loc[
            (
                data[FASE1_DATASET["columns_input_v0"]["col_date"]]
                > end_actual_0
            )
            & (
                data[FASE1_DATASET["columns_input_v0"]["col_date"]]
                <= prev_12_date
            ),
            j,
        ].values

# Repetimos con la misma logica pero cambiando el tramo
real_data_1 = data.loc[
    (data[FASE1_DATASET["columns_input_v0"]["col_date"]] > prev_12_date)
    & (data[FASE1_DATASET["columns_input_v0"]["col_date"]] <= end_actual_date),
    pred_1,
]

# Los pasos siguientes son identicos al anterior pero cambiando los tramos y la informacion que se mete en cada tramo.
for i, j in zip(pred_1[1:], real_columns[1:]):
    if real_data_1[i].sum() == 0:
        real_data_1[i] = data.loc[
            (
                data[FASE1_DATASET["columns_input_v0"]["col_date"]]
                > prev_12_date
            )
            & (
                data[FASE1_DATASET["columns_input_v0"]["col_date"]]
                <= end_actual_date
            ),
            j,
        ].values

real_data_2 = data.loc[
    (data[FASE1_DATASET["columns_input_v0"]["col_date"]] > end_actual_date),
    pred_2,
]

for i, j in zip(pred_2[1:], real_columns[1:]):
    if real_data_2[i].sum() == 0:
        real_data_2[i] = data.loc[
            (
                data[FASE1_DATASET["columns_input_v0"]["col_date"]]
                > end_actual_date
            ),
            j,
        ].values

# Una vez extraidos los dataset con la informacion de los distintos tramos se renombran sus columnas unificandolas
real_data_0.columns = real_columns
real_data_1.columns = real_columns
real_data_2.columns = real_columns

# data_end contiene toda la informacion historica de las columnas anterior a la fecha en la que empezamos a definir los tramos.
# Por eso toda la informacion anterior a la fecha end_actual_0 (fecha donde empieza el primer tramo) es informacion historica
data_end = data.loc[
    (data[FASE1_DATASET["columns_input_v0"]["col_date"]] <= end_actual_0),
    real_columns,
]

# Se introducen todos los dataframes en una lista
dataframes = [data_end, real_data_0, real_data_1, real_data_2]

# Se concatenan todos los dataframes en un unico df
df = pd.concat(dataframes)

# Se crea la variable Rampa
df["rampa"] = (
    df[FASE1_DATASET["columns_input_v0"]["col_demanda_residual"]].shift(1)
    - df[FASE1_DATASET["columns_input_v0"]["col_demanda_residual"]]
)
df = df[1:]

# df["demanda"] = df["demanda"].replace(0, np.nan)


df.to_excel(
     os.path.join(PATHS['LOCAL']['root'], 'datasets', 'dataset_input_v1.xlsx'),
    index=False,
)
