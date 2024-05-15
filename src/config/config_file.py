import os
from datetime import datetime, timedelta
import numpy as np

basepath = os.path.dirname(__file__)  # script directory

# start_date_fase1 = (
#     datetime.now().strftime("%Y-%m-%d")
#     if datetime.now().hour > 14
#     else (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
# )

# date = (
#     (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
#     if datetime.now().hour > 14
#     else datetime.now().strftime("%Y-%m-%d")
# )

start_date_fase1 = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
end_date_fase1 = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
date = datetime.now().strftime("%Y-%m-%d")


DATE_INFO = {
    "date": date,  # fecha de descarga de datos %Y-%m-%d "2024-03-08"
    "update_hour": 10,  # 10,  # para la descarga de datos, si se hace entre las 10 y las 11 poner el valor mas pequeño (10)
    "start_date_fase1": start_date_fase1, #fecha inicio predicciones fase1
    "end_date_fase1": end_date_fase1 #fecha fin predicciones fase1
}

YEAR = str(datetime.strptime(DATE_INFO["date"], "%Y-%m-%d").year)

##################### FASE 1 #########################
FASE1_SETTINGS = {
    "ajuste": 0,  # 0: Sin transformacion; 1: Tope40; 2: Ajuste 40-precio
    "backup": True,  # True: a backup file of web scraping is saved; False: No backup file saved
    "validation_days": 1,  # 1: one day to validate models
    "test_days": 1,  # one day prediction
    "overwrite_fase1_output": True,
    "retrain_arima": True,  # True: If new arima coeficients are desired; False: Use saved model (same order different coefficients)
    "new_base_model": True,  # True: If a new_base_model will be trained (new order wil be found).
}

FASE1_MODELS = {
    "Ridge": {
        "Run_model": True,  # If True model is executed in the comparative, False not executed in the comparative
        # "Run_HT": True,
        # "Name": "Ridge",
        "Params": {"random_state": 101},
        "Params_grid_HT": {"ridge__alpha": np.logspace(-5, 4, 28)},
    },
    "XGBoost": {
        "Run_model": False,
        # "Run_HT": True,
        # "Name": "XGBoost",
        "Params": {"random_state": 101},
        "Params_grid_HT": {
            "n_estimators": [250, 500],
            "max_depth": [1, 3, 4],
            "learning_rate": [0.01, 0.1, 1],
        },
    },
    "RandomForest": {
        "Run_model": False,
        # "Run_HT": True,
        # "Name": "RandomForest",
        "Params": {"random_state": 101},
        "Params_grid_HT": {
            "n_estimators": [250, 500],
            "max_depth": [1, 3, 4],
        },
    },
    "LGBM": {
        "Run_model": True,
        # "Run_HT": True,
        # "Name": "LGBM",
        "Params": {"random_state": 101},
        "Params_grid_HT": {
            # "num_leaves": [24,30,50,70,80],
            "n_estimators": [50, 100, 500],
            "max_depth": [1, 3, 4, 10],
            "learning_rate": [0.01, 0.1, 1],
        },
    },
    "CatBoost": {
        "Run_model": False,
        # "Run_HT": True,
        # "Name": "CatBoost",
        "Params": {"random_state": 101},
        "Params_grid_HT": {
            "n_estimators": [2250, 500],
            "max_depth": [1, 3, 4],
            "learning_rate": [0.01, 0.1, 1],
        },
    },
    "ARIMA": {
        "Run_model": True,
        "params": [
            # [1, 1, 1, 2, 0, 2, 24],
            # [2, 1, 2, 2, 0, 2, 24]
            # [5, 1, 2, 3, 1, 1, 24]
            # [2, 0, 3, 3, 0, 3, 24], #octubre 1
            # [1, 0, 3, 1, 0, 1, 24] #octubre 1 - demanda residual+rampa+gas+co2
            # [1, 0, 3, 1, 0, 1, 24] #octubre 1 - demanda residual+rampa+all_others
            # [3, 0, 3, 1, 0, 1, 24] #octubre 1 - exog escalon
            # [2, 0, 1, 3, 1, 3, 24] #octubre 9 - demanda residual+rampa+gas+co2
            # [2, 0, 1, 3, 1, 3, 24] #octubre 9 - demanda residual+rampa+all_others
            # [3, 0, 2, 3, 1, 3, 24] #octubre 9 - exog_escalon
            # [1, 0, 2, 3, 0, 2, 12], #octubre 2
            # [3, 0, 1, 1, 0, 1, 12], #octubre 18-22
            # [3, 0, 3, 2, 0, 1, 12], #octubre 23-29
            # [3, 0, 2, 1, 0, 3, 12], #octubre 30-noviembre 05
            # [1, 0, 1, 1, 0, 1, 12] #octubre 17
            # [1, 1, 2, 1, 1, 1, 12] #octubre 17 - exog escalon
            # [1, 1, 2, 1, 1, 1, 12] #octubre 17 - demanda residual+rampa+gas+co2
            # [1, 1, 2, 1, 1, 1, 12] #octubre 17 - demanda residual+rampa+all_others
            # [1, 0, 2, 1, 0, 1, 12] #octubre 18
            # [1, 0, 2, 1, 0, 1, 12] #octubre 18 - exog escalon
            # [1, 0, 1, 1, 0, 1, 12] #octubre 18 - demanda residual+rampa+gas+co2
            # [1, 0, 2, 1, 0, 1, 12] #octubre 18 - demanda residual+rampa+all_others
            # [3, 0, 2, 3, 0, 2, 24] #octubre 19
            # [1, 1, 1, 2, 0, 1, 24] #octubre 19 - exog escalon
            # [1, 1, 1, 2, 1, 2, 24] #octubre 19 - demanda residual+rampa+gas+co2
            # [1, 1, 1, 2, 1, 2, 24] #octubre 19 - demanda residual+rampa+all_others
            # [3, 0, 3, 2, 1, 1, 12] #octubre 20
            # [3, 1, 1, 3, 0, 1, 12] #octubre 20 - exog escalon
            # [3, 1, 1, 3, 0, 1, 12] #octubre 20 - demanda residual+rampa+gas+co2
            # [1, 0, 1, 2, 1, 1, 12] #octubre 20 - demanda residual+rampa+all_others
            # [1, 1, 1, 2, 1, 3, 24] #octubre 21
            # [1, 1, 3, 1, 1, 1, 12] #octubre 21 - exog escalon
            # [1, 1, 1, 3, 1, 1, 12] #octubre 21 - demanda residual+rampa+gas+co2
            # [1, 1, 1, 3, 1, 1, 12] #octubre 21 - demanda residual+rampa+all_others
            # [1, 1, 3, 1, 1, 1, 12] #octubre 22 - exog escalon
            # [1, 0, 1, 3, 1, 2, 24] #octubre 22 - demanda residual+rampa+gas+co2
            # [1, 0, 1, 3, 1, 2, 24] #octubre 22 - demanda residual+rampa+all_others
            # [1, 0, 3, 1, 0, 1, 12] #noviembre 01
            # [3, 0, 1, 1, 0, 1, 12] #noviembre 01 - exog escalon
            # [3, 0, 1, 1, 0, 1, 12] #noviembre 01- demanda residual+rampa+gas+co2
            # [3, 0, 1, 1, 0, 1, 12] #noviembre 01 - demanda residual+rampa+all_others
            # [3, 1, 1, 1, 1, 2, 12] #noviembre 02
            # [2, 1, 1, 2, 1, 2, 12] #noviembre 02 - exog escalon
            # [2, 1, 1, 2, 1, 2, 12] #noviembre 02- demanda residual+rampa+gas+co2
            # [2, 1, 1, 2, 1, 2, 12] #noviembre 02 - demanda residual+rampa+all_others
            # [3, 1, 2, 1, 0, 1, 12] #noviembre 03
            # [3, 1, 3, 3, 0, 3, 12] #noviembre 03 - exog escalon
            # [3, 1, 3, 2, 0, 3, 12] #noviembre 03- demanda residual+rampa+gas+co2
            # [2, 1, 3, 1, 0, 2, 12] #noviembre 03 - demanda residual+rampa+all_others
            # [1, 1, 2, 1, 0, 3, 12] #noviembre 04
            # [2, 1, 1, 3, 0, 1, 12] #noviembre 04 - exog escalon
            # [2, 1, 1, 3, 0, 1, 12] #noviembre 04 - demanda residual+rampa+gas+co2
            # [1, 1, 1, 1, 0, 3, 12] #noviembre 04 - demanda residual+rampa+all_others
            # [1, 1, 2, 1, 1, 1, 12] #octubre 17 - demanda residual+rampa+all_others
            # [3, 1, 1, 1, 0, 3, 24] #noviembre 05
            # [4, 1, 2, 1, 1, 1, 24],
            # [1, 1, 5, 2, 1, 1, 12],
            [3, 0, 3, 3, 1, 2, 24]  # enero 05 2024
        ],
    },
}

##################### FASE 2 #########################

##################### FASE 3 #########################

##################### SWAT #########################
SWAT = {
    "lead": 0,
    "mode": "automodel",
    "alpha": 0.05,
    "filetype": "csv",
    "format_date": "DATETIME19.",
    "informat_date": "DATETIME19.",
}
