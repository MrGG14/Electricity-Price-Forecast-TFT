"""

    PoC Bidding Energia: Updates dataset_input_v0

    Last version May 2022

    Author: Hector Andrey Cortazar

"""

# import sys
# import os
# Access files in different directories (only during execution)
# basepath = os.path.dirname(__file__)  # script directo
# sys.path.insert(1, os.path.join(basepath, ".."))

import pandas as pd
from preprocessing.helper_pd_01_webscraping_fase_1 import (
    esios_update,
    gas_price_update,
    co2_price_update,
)

from utils.utils_file import load_xlsx
from utils.logger_utils import logger as logger1
from config.metadata import (
    FASE1_DATASET,
    TOKEN,
    PATHS,
)

cols_input_v0 = [
    FASE1_DATASET["columns_input_v0"][key]
    for key in FASE1_DATASET["columns_input_v0"].keys()
]


# TODO: Add gestion de errores -> Try Except Finally
def update_data_model(
    date,
    today_hour,
    path,
    download_path=PATHS["LOCAL"]["download_path"],
    token=TOKEN,
):
    """Update dataset_input_v0

    Parameters
    ----------
    date : str
        date at which updated is requested
    today_hour : _type_
        time at which updated is requested
    path : str
        path where dataset is located
    driver_path : str, optional
        path where chrome web driver is located, by default PATHS["LOCAL"]["driver_path"]
    download_path :str, optional
        downloads path, by default PATHS["LOCAL"]["download_path"]
    token : str, optional
        token to access to esios API, by default TOKEN

    Returns
    -------
    df
        updated dataset_input_v0
    """

    old_df = load_xlsx(path)
    logger1.info("Dataset loaded")
    esios_data = esios_update(date, today_hour, old_df, token)
    logger1.info("Esios data updated")
    gas_data = gas_price_update(
        date,
        old_df,
        download_path,
    ).reset_index(drop=True)
    logger1.info("Gas price updated")
    co2_data = co2_price_update(
        date,
        old_df,
        download_path,
    ).reset_index(drop=True)
    logger1.info("CO2 price updated")

    new_input = pd.concat(
        [
            esios_data,
            gas_data[
                [
                    FASE1_DATASET["columns_input_v0"]["col_gas"],
                    FASE1_DATASET["columns_input_v0"]["col_gas_prev24"],
                    FASE1_DATASET["columns_input_v0"]["col_gas_prev48"],
                ]
            ],
            co2_data[
                [
                    FASE1_DATASET["columns_input_v0"]["col_co2"],
                    FASE1_DATASET["columns_input_v0"]["col_co2_prev24"],
                    FASE1_DATASET["columns_input_v0"]["col_co2_prev48"],
                ]
            ],
        ],
        axis=1,
    ).reset_index(drop=True)
    new_input = new_input[cols_input_v0]
    logger1.info("Dataset_v0 updated")

    return new_input
