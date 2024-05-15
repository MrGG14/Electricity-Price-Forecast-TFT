import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
import os
from config.metadata import FASE1_DATASET
from datetime import datetime, timedelta
from utils.logger_utils import logger as logger1
from config.metadata import FASE1_DATASET, PATHS

__all__ = ["error_metrics"]


def error_metrics(actual, predicted):
    """Get errors (SMAPE, MAPE, WAPE, RMSE, MAE) between actual and predicted values

    Parameters
    ----------
    actual: pandas.Series

    predicted: pandas.Series

    Returns
    -------
    Dictionary with errors (SMAPE, MAPE, WAPE, RMSE, MAE) as keys
    """

    try:
        actual = np.array(actual)
        predicted = np.array(predicted)

        # smape error
        smape_term = abs(predicted - actual) / (abs(actual) + abs(predicted))
        smape_term = [0 if np.isnan(term) else term for term in smape_term]
        smape = round(100 * np.mean(smape_term), 2)

        # mape error
        mape = (
            "Indefinido"
            if any(actual == 0)
            else (round(np.mean(abs((predicted - actual) / actual)) * 100, 2))
        )

        # mae error
        mae = round(np.mean(np.abs(predicted - actual)), 2)

        # wape error
        wape = (
            (
                round(
                    (np.sum(abs(actual - predicted)) / np.sum(abs(actual)) * 100),
                    2,
                )
            )
            if np.sum(abs(actual)) != 0
            else "Indefinido"
        )

        rmse = mean_squared_error(actual, predicted)

        mav = sum(abs((actual / max(actual)) - (predicted / max(predicted))))

        errors = {
            "SMAPE": smape,
            "MAPE": mape,
            "WAPE": wape,
            "RMSE": rmse,
            "MAE": mae,
            "MAV": mav,
        }
    except:
        errors = {
            "SMAPE": np.nan,
            "MAPE": np.nan,
            "WAPE": np.nan,
            "RMSE": np.nan,
            "MAE": np.nan,
            "MAV": np.nan,
        }

    return errors


def get_error_diario(df_results, col_results, error):
    """Get daily errors for a model (col_results)

    Parameters
    ----------
    df_results: DataFrame

    col_results: str

    error: str

    Returns
    -------
    DataFrame
    """

    df_results["date"] = df_results[
        FASE1_DATASET["columns_input_v0"]["col_date"]
    ].apply(lambda x: x.date())
    dates = np.unique(df_results["date"])
    df_error = pd.DataFrame(
        columns=[FASE1_DATASET["columns_input_v0"]["col_date"], error]
    )

    for date in dates:
        df_temp = df_results.iloc[np.where(df_results["date"] == date)]
        get_error = error_metrics(
            df_temp[FASE1_DATASET["columns_input_v0"]["col_target"]],
            df_temp[col_results],
        )[error]
        temp_error = pd.DataFrame(
            {
                FASE1_DATASET["columns_input_v0"]["col_date"]: df_temp.iloc[0, 0],
                error: [get_error],
            }
        )
        df_error = pd.concat([df_error, temp_error])

    return df_error


def update_preds_history(new_input: pd.DataFrame):
    """Includes last published SPOT price to preds_history.xlsx and NTTDATA_PrecioSPOT_preds.xlsx and gets error metrics

    Parameters
    ----------
    new_input : pd.DataFrame
        dataset_v0
    """
    today = datetime.now()
    # today = datetime.strptime('2024-03-27', '%Y-%m-%d')
    today_i = today.strftime("%Y-%m-%d 00:00:00")
    today_f = today.strftime("%Y-%m-%d 23:00:00")

    # tomorrow = datetime.now() + timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    tomorrow_i = today_i  # today = tomorrow pq hacemos esto por la mañana, aunque se deebria hacer por la tarde cuando obtengamos el precio SPOT por la tarde
    tomorrow_f = today_f

    real_vals = new_input[
        (new_input["fechaHora"] >= tomorrow_i) & (new_input["fechaHora"] <= tomorrow_f)
    ]
    real_vals = real_vals[["fechaHora", "precio_spot"]]
    real_vals = real_vals.rename(columns={"precio_spot": "precio_real"})
    real_vals.set_index("fechaHora", inplace=True)

    historic_df = pd.read_excel(
        os.path.join(
            PATHS["LOCAL"]["root"],
            PATHS["LOCAL"]["output_fase1"],
            "backup_datasets_output",
            "preds_history.xlsx",
        )
    )

    historic_df.set_index("fechaHora", inplace=True)
    filter = (historic_df.index >= tomorrow_i) & (historic_df.index <= tomorrow_f)
    historic_df.loc[filter, "precio_real"] = real_vals
    historic_df.loc[filter, "diff"] = (
        historic_df.loc[filter, "precio_real"] - historic_df.loc[filter, "precio_pred"]
    )
    try:
        historic_df.loc[filter, "perc_err"] = (
            abs(
                historic_df.loc[filter, "precio_pred"]
                - historic_df.loc[filter, "precio_real"]
            )
            / historic_df.loc[filter, "precio_pred"]
        ) * 100
    except:
        historic_df.loc[filter, "perc_err"] = "Indefinido"
        logger1.info("No percentaje error. Spot price = 0, cant do division by 0")

    errors = error_metrics(
        historic_df.loc[filter, "precio_real"],
        historic_df.loc[filter, "precio_pred"],
    )

    mape_results = errors["MAPE"]
    historic_df.loc[filter, "MAPE"] = mape_results

    mae_results = errors["MAE"]
    historic_df.loc[filter, "MAE"] = mae_results

    wape_results = errors["WAPE"]
    historic_df.loc[filter, "WAPE"] = wape_results

    mav_results = errors["MAV"]
    historic_df.loc[filter, "MAV"] = mav_results

    historic_df.to_excel(
        os.path.join(
            PATHS["LOCAL"]["root"],
            PATHS["LOCAL"]["output_fase1"],
            "backup_datasets_output",
            "preds_history.xlsx",
        ),
        index=True,
    )
    logger1.info("Internal prediction history updated with real values")

    historic_df.drop(columns=["model", "perc_err", "MAPE", "WAPE", "MAV"], inplace=True)

    historic_df.to_excel(
        os.path.join(
            PATHS["LOCAL"]["root"],
            PATHS["LOCAL"]["output_fase1"],
            "Pruebas",
            # TODO pasar como arg que se configure desde main o config
            "202404 Pruebas Total-Axpo",
            f"NTTDATA_PrecioSPOT_preds.xlsx",  # {datetime.now().strftime('%Y%m%d')}
        ),
        index=True,
    )
    logger1.info("Client prediction history updated with real values")
