"""

    PoC Bidding Energia: Supports update_dataset_input_v0.py to update dataset_input_v0 

    Last version May 2022

    Author: Hector Andrey Cortazar

"""

import pandas as pd
import requests
from datetime import datetime, timedelta
from functools import reduce
import numpy as np
import time
import os
import sys
import glob

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options as FirefoxOptions


basepath = os.path.dirname(__file__)  # script directory
sys.path.insert(1, os.path.join(basepath, ".."))

from config.metadata import (
    FASE1_DATASET,
    FASE1_DATA_SCRAPING,
    PATHS,
    dict_months,
)
from utils.logger_utils import logger as logger1


def get_driver(local=True):

    chrome_options = ChromeOptions()
    chrome_options.headless = False

    driver = webdriver.Chrome(
        options=chrome_options,
        service=Service(executable_path=PATHS["LOCAL"]["chrome_driver_path"]),
    )
    logger1.info("WebDriverManager successfully loaded")

    return driver


def get_esios_data(
    start_date,
    end_date,
    indicator,
    token=FASE1_DATA_SCRAPING["token_esios"],
    var_name="value",
):
    """Download data from esios API

    Parameters
    ----------
    start_date : str
        date to start data download
    end_date : str
        date to stop data download
    indicator : str
        esios technology indicator
    token : str, optional
        token to access to esios API, by default TOKEN
    var_name : str, optional
        thecnology name, by default "value"

    Returns
    -------
    df
        _description_
    """

    start_date_1 = f"{start_date} 00:00:00"
    end_date = f"{end_date} 23:59:00"

    date_format = "%Y-%m-%d %H:%M:%S"

    start_date_1 = datetime.strptime(start_date_1, date_format)

    parameters = {
        "start_date": start_date_1,
        "end_date": end_date,
        "locale": "es",
        "time_agg": "average",
        "time_trunc": "hour",
        "geo_agg": "average",
        # "geo_id": 3,
        # "geo_trunc": "country",
    }

    # Definition of the url
    url = FASE1_DATA_SCRAPING["url_esios"] + str(indicator)

    # Log informative message
    logger1.info(f"esios_url: {url}")

    # request from the url with the defined parameters
    response = requests.get(
        url,
        params=parameters,
        headers=FASE1_DATA_SCRAPING["headers_esios"],
        verify=False,
    )

    # Creation of first dataframe
    df = pd.DataFrame(response.json()["indicator"]["values"])

    if str(indicator) == "600":
        df = df.iloc[np.where(df["geo_name"] == "España")[0]].reset_index(
            drop=True
        )

    else:
        # df = df.iloc[np.where(df["geo_name"] == "Península")[0]].reset_index(drop=True)
        df = df.iloc[
            np.where(
                df["geo_ids"] == pd.Series([[8741] for i in range(len(df))])
            )[0]
        ].reset_index(drop=True)

    # Changing the format of the date column
    df["datetime"] = pd.to_datetime(
        df["datetime"], format=date_format, utc=True
    )

    # Sometimes there is incompleted data concatenated, to avoid mistakes, we create a timeline from the start date and end date and do a left join with previous info
    ts = pd.DataFrame(
        pd.date_range(start_date, end=end_date, freq="H", tz="Africa/Ceuta")
    )

    # rename of ts column
    ts.columns = ["0"]

    # left join + renaming of columns + fill missing values with 0
    df_aux = (
        ts.merge(df, left_on="0", right_on="datetime", how="left")
        .rename(
            columns={
                "value": var_name,
                "0": FASE1_DATASET["columns_input_v0"]["col_date"],
            }
        )[[var_name, FASE1_DATASET["columns_input_v0"]["col_date"]]]
        .fillna(0)
    )

    # Creation of variable "dia" and feature enginering
    df_aux["dia"] = df_aux[
        FASE1_DATASET["columns_input_v0"]["col_date"]
    ].dt.strftime("%Y-%m-%d")

    df_aux[FASE1_DATASET["columns_input_v0"]["col_date"]] = df_aux[
        FASE1_DATASET["columns_input_v0"]["col_date"]
    ].apply(lambda x: str(x)[:-6])

    df_aux[FASE1_DATASET["columns_input_v0"]["col_date"]] = df_aux[
        FASE1_DATASET["columns_input_v0"]["col_date"]
    ].apply(lambda x: datetime.strptime(x, date_format))

    return df_aux


def update_columns(
    old_input_esios,
    date,
    today_hour,
    var_name,
    indicator,
    column_type,
    token=FASE1_DATA_SCRAPING["token_esios"],
):
    """Updates a column from old_input_esios aaccording to column_type

    Returns
    -------
    df
        two column df with date and updated column
    """
    date_format = "%Y-%m-%d %H:%M:%S"

    last_day_data = old_input_esios[
        FASE1_DATASET["columns_input_v0"]["col_date"]
    ][
        len(old_input_esios) - 1
    ]  # ultimo dia en la data-corresponde a un dia posterior a la actualizacion

    last_day_model_update = last_day_data - timedelta(
        days=1
    )  # dia en que se descargaron los datos por ultima vez

    today_date = datetime.strptime(date, "%Y-%m-%d")
    last_hour_today = datetime.strptime(
        date + " 23:59:00", date_format
    )  # fecha de hoy a última hora del día

    update_hour = datetime.strptime(
        date + " " + str(today_hour) + ":00:00", date_format
    )

    # Descarga de datos de esios

    start_date = (
        str(last_day_model_update.year)
        + "-"
        + str(last_day_model_update.month)
        + "-"
        + str(last_day_model_update.day)
    )
    end_date = today_date + timedelta(
        days=1
    )  # se suma 1 dia porque en get_esios a 'end_date' se le pone 00:00:00
    end_date = (
        str(end_date.year)
        + "-"
        + str(end_date.month)
        + "-"
        + str(end_date.day)
    )

    downloaded_data = get_esios_data(
        start_date,
        end_date,
        token=token,
        indicator=indicator,
        var_name=var_name,
    )

    if column_type == "real":
        cols_prevision = [
            FASE1_DATASET["columns_input_v0"]["col_demanda_residual"],
            FASE1_DATASET["columns_input_v0"]["col_eolic_prevision"],
            FASE1_DATASET["columns_input_v0"]["col_solar_prevision"],
            FASE1_DATASET["columns_input_v0"]["col_demand_prevision"],
        ]

        if var_name == FASE1_DATASET["columns_input_v0"]["col_target"]:
            data_d = downloaded_data.iloc[
                np.where(
                    downloaded_data[
                        FASE1_DATASET["columns_input_v0"]["col_date"]
                    ]
                    <= last_hour_today + timedelta(days=1)
                )[0],
            ]

            data_d.loc[
                np.where(
                    data_d[FASE1_DATASET["columns_input_v0"]["col_date"]]
                    > last_hour_today
                )[0],
                FASE1_DATASET["columns_input_v0"]["col_target"],
            ] = np.nan

        elif var_name in cols_prevision:
            data_d = downloaded_data.iloc[
                np.where(
                    downloaded_data[
                        FASE1_DATASET["columns_input_v0"]["col_date"]
                    ]
                    <= last_hour_today + timedelta(days=1)
                )[0],
            ]

        else:
            data_d = downloaded_data.iloc[
                np.where(
                    downloaded_data[
                        FASE1_DATASET["columns_input_v0"]["col_date"]
                    ]
                    <= update_hour
                )[0],
            ]

        data_d.columns = [
            var_name,
            FASE1_DATASET["columns_input_v0"]["col_date"],
            "dia",
        ]

        old_data = old_input_esios.iloc[
            np.where(
                old_input_esios[FASE1_DATASET["columns_input_v0"]["col_date"]]
                <= last_day_model_update - timedelta(days=1)
            )[0]
        ]

        real_update = pd.concat(
            [
                old_data[
                    [FASE1_DATASET["columns_input_v0"]["col_date"], var_name]
                ],
                data_d[
                    [FASE1_DATASET["columns_input_v0"]["col_date"], var_name]
                ],
            ]
        ).reset_index(drop=True)
        real_update.columns = [
            FASE1_DATASET["columns_input_v0"]["col_date"],
            var_name,
        ]

        return real_update

    elif column_type == "prev12":
        days_diff = today_date.date() - last_day_data.date()
        days_diff = days_diff.days

        expected_d = downloaded_data.iloc[
            np.where(
                downloaded_data[FASE1_DATASET["columns_input_v0"]["col_date"]]
                <= last_hour_today
            )[0],
        ]
        start_prev12 = expected_d[
            FASE1_DATASET["columns_input_v0"]["col_date"]
        ][0] + timedelta(days=1)

        if days_diff > 0:
            expected_d.loc[
                np.where(
                    expected_d[FASE1_DATASET["columns_input_v0"]["col_date"]]
                    <= update_hour
                )[0]
            ] = np.nan

            expected_d = expected_d.loc[
                np.where(
                    expected_d[FASE1_DATASET["columns_input_v0"]["col_date"]]
                    >= start_prev12
                )[0],
                :,
            ]
            expected_d.columns = [
                var_name,
                FASE1_DATASET["columns_input_v0"]["col_date"],
                "dia",
            ]

            old_prev12 = old_input_esios.iloc[
                np.where(
                    old_input_esios[
                        FASE1_DATASET["columns_input_v0"]["col_date"]
                    ]
                    < start_prev12
                )[0]
            ]
        else:
            expected_d = expected_d.loc[
                np.where(
                    expected_d[FASE1_DATASET["columns_input_v0"]["col_date"]]
                    > update_hour
                )[0],
                :,
            ]
            expected_d.columns = [
                var_name,
                FASE1_DATASET["columns_input_v0"]["col_date"],
                "dia",
            ]
            old_prev12 = old_input_esios.iloc[
                np.where(
                    old_input_esios[
                        FASE1_DATASET["columns_input_v0"]["col_date"]
                    ]
                    <= update_hour
                )[0]
            ]

        new_prev12 = pd.concat(
            [
                old_prev12[
                    [FASE1_DATASET["columns_input_v0"]["col_date"], var_name]
                ],
                expected_d[
                    [FASE1_DATASET["columns_input_v0"]["col_date"], var_name]
                ],
            ]
        ).reset_index(drop=True)
        new_prev12.columns = [
            FASE1_DATASET["columns_input_v0"]["col_date"],
            var_name,
        ]

        return new_prev12

    elif column_type == "prev36":
        expected_d1 = downloaded_data.iloc[
            np.where(
                (
                    downloaded_data[
                        FASE1_DATASET["columns_input_v0"]["col_date"]
                    ]
                    > last_hour_today
                )
                & (
                    downloaded_data[
                        FASE1_DATASET["columns_input_v0"]["col_date"]
                    ]
                    <= last_hour_today + timedelta(days=1)
                )
            )[0],
        ]
        expected_d1.columns = [
            var_name,
            FASE1_DATASET["columns_input_v0"]["col_date"],
            "dia",
        ]
        new_prev36 = pd.concat(
            [
                old_input_esios[
                    [FASE1_DATASET["columns_input_v0"]["col_date"], var_name]
                ],
                expected_d1[
                    [FASE1_DATASET["columns_input_v0"]["col_date"], var_name]
                ],
            ]
        ).reset_index(drop=True)
        new_prev36.columns = [
            FASE1_DATASET["columns_input_v0"]["col_date"],
            var_name,
        ]

        return new_prev36


def esios_update(
    date, today_hour, old_df, token=FASE1_DATA_SCRAPING["token_esios"]
):
    """Update esios historical prices and forecasts prev12, prev36

    Parameters
    ----------
    date : str
        date at which updated is requested
    today_hour : int
        hour at which updated is requested
    old_df : df
        dataset_input_v0 to be updated
    token : str
        token to access to esios API, by default TOKEN

    Returns
    -------
    df
        updated esios dataset_input_v0 columns
    """

    old_input_esios = old_df
    old_input_esios = old_input_esios[
        [
            FASE1_DATASET["columns_input_v0"][key]
            for key in FASE1_DATASET["columns_input_v0"].keys()
        ]
    ].copy()

    # update real variables
    spot_price = update_columns(
        old_input_esios,
        date,
        today_hour,
        FASE1_DATASET["columns_input_v0"]["col_target"],
        FASE1_DATA_SCRAPING["indicator_dict_esios"]["col_target"],
        "real",
        token,
    )

    real_vars = [
        (
            FASE1_DATA_SCRAPING["indicator_dict_esios"]["col_demand"],
            FASE1_DATASET["columns_input_v0"]["col_demand"],
        ),
        (
            FASE1_DATA_SCRAPING["indicator_dict_esios"]["col_eolic"],
            FASE1_DATASET["columns_input_v0"]["col_eolic"],
        ),
        (
            FASE1_DATA_SCRAPING["indicator_dict_esios"]["col_solar"],
            FASE1_DATASET["columns_input_v0"]["col_solar"],
        ),
        (
            FASE1_DATA_SCRAPING["indicator_dict_esios"]["col_nuclear"],
            FASE1_DATASET["columns_input_v0"]["col_nuclear"],
        ),
        (
            FASE1_DATA_SCRAPING["indicator_dict_esios"]["col_combined_cycle"],
            FASE1_DATASET["columns_input_v0"]["col_combined_cycle"],
        ),
        (
            FASE1_DATA_SCRAPING["indicator_dict_esios"]["col_cogeneration"],
            FASE1_DATASET["columns_input_v0"]["col_cogeneration"],
        ),
        (
            FASE1_DATA_SCRAPING["indicator_dict_esios"]["col_hydraulic"],
            FASE1_DATASET["columns_input_v0"]["col_hydraulic"],
        ),
        (
            FASE1_DATA_SCRAPING["indicator_dict_esios"]["col_renewable"],
            FASE1_DATASET["columns_input_v0"]["col_renewable"],
        ),
        (
            FASE1_DATA_SCRAPING["indicator_dict_esios"]["col_not_renewable"],
            FASE1_DATASET["columns_input_v0"]["col_not_renewable"],
        ),
        (
            FASE1_DATA_SCRAPING["indicator_dict_esios"]["col_co2_free"],
            FASE1_DATASET["columns_input_v0"]["col_co2_free"],
        ),
        (
            FASE1_DATA_SCRAPING["indicator_dict_esios"][
                "col_demanda_residual"
            ],
            FASE1_DATASET["columns_input_v0"]["col_demanda_residual"],
        ),
        (
            FASE1_DATA_SCRAPING["indicator_dict_esios"]["col_eolic_prevision"],
            FASE1_DATASET["columns_input_v0"]["col_eolic_prevision"],
        ),
        (
            FASE1_DATA_SCRAPING["indicator_dict_esios"]["col_solar_prevision"],
            FASE1_DATASET["columns_input_v0"]["col_solar_prevision"],
        ),
        (
            FASE1_DATA_SCRAPING["indicator_dict_esios"][
                "col_demand_prevision"
            ],
            FASE1_DATASET["columns_input_v0"]["col_demand_prevision"],
        ),
    ]
    real_updates = spot_price.copy()
    for key, var_name in real_vars:
        real_var_update = update_columns(
            old_input_esios, date, today_hour, var_name, key, "real", token
        )

        real_updates = pd.concat(
            [real_updates, real_var_update[var_name]], axis=1
        )

    # update prev12 variables
    prev12_vars = [
        (
            FASE1_DATA_SCRAPING["indicator_dict_esios"]["col_demand_prev12"],
            FASE1_DATASET["columns_input_v0"]["col_demand_prev12"],
        ),
        (
            FASE1_DATA_SCRAPING["indicator_dict_esios"]["col_eolic_prev12"],
            FASE1_DATASET["columns_input_v0"]["col_eolic_prev12"],
        ),
        (
            FASE1_DATA_SCRAPING["indicator_dict_esios"]["col_solar_prev12"],
            FASE1_DATASET["columns_input_v0"]["col_solar_prev12"],
        ),
    ]
    prev12_updates = pd.DataFrame()
    for key, var_name in prev12_vars:
        prev12_var_update = update_columns(
            old_input_esios, date, today_hour, var_name, key, "prev12", token
        )
        prev12_updates = pd.concat([prev12_updates, prev12_var_update], axis=1)

    prev12_updates = (
        prev12_updates.T.drop_duplicates().T
    )  # drop duplicates columns 'FASE1_DATASET["columns_input_v0"]["col_date"]'

    # update prev36 variables
    prev36_vars = [
        (
            FASE1_DATA_SCRAPING["indicator_dict_esios"]["col_demand_prev36"],
            FASE1_DATASET["columns_input_v0"]["col_demand_prev36"],
        ),
        (
            FASE1_DATA_SCRAPING["indicator_dict_esios"]["col_eolic_prev36"],
            FASE1_DATASET["columns_input_v0"]["col_eolic_prev36"],
        ),
        (
            FASE1_DATA_SCRAPING["indicator_dict_esios"]["col_solar_prev36"],
            FASE1_DATASET["columns_input_v0"]["col_solar_prev36"],
        ),
    ]
    prev36_updates = pd.DataFrame()
    for key, var_name in prev36_vars:
        prev36_var_update = update_columns(
            old_input_esios, date, today_hour, var_name, key, "prev36", token
        )
        prev36_updates = pd.concat([prev36_updates, prev36_var_update], axis=1)

    prev36_updates = (
        prev36_updates.T.drop_duplicates().T
    )  # drop duplicates columns 'FASE1_DATASET["columns_input_v0"]["col_date"]'

    # update dataset_input
    new_inputs = [real_updates, prev12_updates, prev36_updates]
    esios_update = reduce(
        lambda left, right: pd.merge(
            left,
            right,
            on=[FASE1_DATASET["columns_input_v0"]["col_date"]],
            how="outer",
        ),
        new_inputs,
    )
    esios_update = esios_update.drop_duplicates()
    esios_update = esios_update.reset_index(drop=True)

    return esios_update


def get_gas_data(
    date,
    download_path=PATHS["LOCAL"]["download_path"],
):
    """Download historical gas prices from MIBGAS web page

    Parameters
    ----------
    date : str
        date at which updated is requested
    driver_path : str, optional
        path where chrome web driver is located, by default PATHS["LOCAL"]["driver_path"]
    download_path :str, optional
        downloads path, by default PATHS["LOCAL"]["download_path"]

    Returns
    -------
    dictionary
        dictionary with historical gas price, current gas price, and current date
    """
    # Date: today_date with formating: %Y-%m-%d. This is needed to identify if it is a weekend or not.
    date = date + " 00:00:00"
    today_date = datetime.strptime(date, "%Y-%m-%d 00:00:00")
    today_name = today_date.strftime("%A")
    year = str(today_date.year)

    # Passing the url we are going to get the data from
    driver = get_driver()
    driver.get(FASE1_DATA_SCRAPING["url_gas"])

    # Download of the data if it is not weekend
    if today_name != "Saturday" or today_name != "Sunday":
        # This first 3 rows extract the gas data price from today
        change_row = driver.find_element(
            by=By.CLASS_NAME, value="row.expandable"
        )

        date_gas = change_row.find_element(
            by=By.CLASS_NAME, value="td.delivary"
        ).text

        price_gas = change_row.find_element(
            by=By.CLASS_NAME, value="td.price"
        ).text

        # This rows extract the price data for tomorrow:
        # 1. definition of the driver again
        # 2. find the dropdown table
        # 3. do scroll down to that table
        # 4. wait 5 second and click on the table
        # 5. extract tomorrow's price

        # driver = get_driver()

        # driver.get(FASE1_DATA_SCRAPING["url_gas"])
        reject_cookies = driver.find_element(
            by=By.XPATH,
            value='//*[@id="cookiesjsr"]/div/div/div[2]/button[2]',
        )
        reject_cookies.click()

        open_table = driver.find_element(
            By.XPATH, '//*[@class="price-table-body"]/div[2]'
        )

        driver.execute_script("window.scrollTo(0, 800)")
        time.sleep(5)
        open_table.click()
        identify_rows = driver.find_element(
            by=By.CLASS_NAME, value="child-row-group"
        )
        price_gas_tomorrow = identify_rows.find_element(
            by=By.XPATH,
            value='//*[@class="price-table-body"]/div[2]/div[2]/div[1]/div[3]',
        ).text

    else:
        change_row = driver.find_elements(by=By.CLASS_NAME, value="row-group")

        date_gas = (
            change_row[2]
            .find_element(by=By.CLASS_NAME, value="td.delivary")
            .text
        )
        price_gas = (
            change_row[2].find_element(by=By.CLASS_NAME, value="td.price").text
        )

    try:
        date_parsed = datetime.strptime((year + "/" + date_gas), "%Y/%d/%m")
    except:
        date_parsed = ""

    try:
        price_parsed = float(price_gas.replace(",", "."))
    except:
        logger1.warning("No gas data for today.")
    try:
        price_tomorrow_parsed = float(price_gas_tomorrow.replace(",", "."))
    except:
        price_tomorrow_parsed = ""

    if type(price_gas_tomorrow) == int or type(price_gas_tomorrow) == float:
        price_gas_tomorrow = price_gas_tomorrow
    else:
        logger1.warning("No gas price for tomorrow. Using price of today.")
        price_gas_tomorrow = price_gas

    # Delete previous download

    file_name = FASE1_DATA_SCRAPING["gas_file_name"]
    file_name = os.path.join(download_path, file_name)

    xslx_files = glob.glob(download_path + "/*.xlsx")

    if file_name in xslx_files:
        os.remove(file_name)

    # Descargar histórico
    get_file_path = FASE1_DATA_SCRAPING["url_gas_2"]
    driver.get(get_file_path)
    try:
        reject_cookies = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "cookiesjsr-btn important denyAll")
            )
        )  # Reject Cookies
        reject_cookies.click()

    except:
        button = driver.find_element(by=By.PARTIAL_LINK_TEXT, value=".xlsx")
        driver.execute_script("window.scrollTo(0, 800)")
        button.click()
        time.sleep(20)

    try:
        # before 2023
        df_gas_mibgas = pd.read_excel(
            file_name, sheet_name="Indices", usecols=[0, 1, 2]
        )
        df_gas_mibgas = df_gas_mibgas.loc[df_gas_mibgas.Area == "ES"]
    except:
        # 2023 and forth

        df_gas_mibgas = pd.read_excel(
            file_name,
            sheet_name="MIBGAS Indexes",
            usecols=[0, 3],
        )

    driver.close()
    return {
        "gas_price_historical": df_gas_mibgas,
        "gas_price_today": price_parsed,
        "download_date": date_parsed,
        "gas_price_tomorrow": price_tomorrow_parsed,
    }


def gas_price_update(
    date,
    old_df,
    download_path=PATHS["LOCAL"]["download_path"],
):
    """Update historical gas price and forecasts prev24, prev48

    Parameters
    ----------
    date : str
        date at which updated is requested
    old_df : df
        dataset_input_v0 to be updated
    driver_path : str, optional
        path where chrome web driver is located, by default PATHS["LOCAL"]["driver_path"]
    download_path :str, optional
        downloads path, by default PATHS["LOCAL"]["download_path"]

    Returns
    -------
    df
        updated gas dataset_input_v0 columns
    """
    # date: today date. format %Y-%m-%d

    date_format = "%Y-%m-%d %H:%M:%S"
    old_input_gas = old_df[
        [
            FASE1_DATASET["columns_input_v0"]["col_date"],
            FASE1_DATASET["columns_input_v0"]["col_gas"],
            FASE1_DATASET["columns_input_v0"]["col_gas_prev24"],
            FASE1_DATASET["columns_input_v0"]["col_gas_prev48"],
        ]
    ]

    # El precio_gas del ultimo dia de la data, es una previsión, se deben cambiar estos datos por los reales.
    last_day_data = old_input_gas[
        FASE1_DATASET["columns_input_v0"]["col_date"]
    ][
        len(old_input_gas) - 1
    ]  # ultimo dia en la data-corresponde a un dia posterior a la actualizacion
    last_day_model_update = last_day_data - timedelta(
        days=1
    )  # dia en que se descargaron los datos por ultima vez
    today_date = datetime.strptime(date, "%Y-%m-%d")

    # data con precios reales hasta la ultima actualizacion (last_day_model_update)
    gas_real_price = old_input_gas.iloc[
        np.where(
            old_input_gas[FASE1_DATASET["columns_input_v0"]["col_date"]]
            <= last_day_model_update - timedelta(days=1)
        )[0],
    ]

    # obtener historico de precios

    gas_data_dict = get_gas_data(
        date,
        download_path,
    )

    # gas_data_dict = scrap_gas
    gas_price_hist = gas_data_dict["gas_price_historical"]

    try:
        gas_price_hist.columns = [
            "fechaDia",
            "Area",
            FASE1_DATASET["columns_input_v0"]["col_gas"],
        ]
    except:
        # 2023 and forth
        gas_price_hist.columns = [
            "fechaDia",
            FASE1_DATASET["columns_input_v0"]["col_gas"],
        ]

    gas_price_tomorrow = gas_data_dict["gas_price_tomorrow"]

    date_now = str(time.strftime("%Y-%m-%d"))
    if date == date_now:
        gas_price_today = gas_data_dict["gas_price_today"]

    else:
        gas_price_today = gas_price_hist.iloc[
            np.where(gas_price_hist["fechaDia"] == date)[0],
        ].reset_index(drop=True)

        try:
            gas_price_today = gas_price_today[
                FASE1_DATASET["columns_input_v0"]["col_gas"]
            ][0]
        except:
            logger1.error(
                "Please check updating date. Dates from MIBGAS_Data file doesn't match with requested date."
            )
            raise
    # filtrar fechas pendientes de actualizar el precio real

    # data en el excel descargado de la pagina
    gas_price_to_update = gas_price_hist.iloc[
        np.where(
            (
                gas_price_hist["fechaDia"]
                > last_day_model_update - timedelta(days=1)
            )
            & (gas_price_hist["fechaDia"] < today_date)
        )
    ]

    # Se actualizan los precios para los dias desde un dia antes de la ultima descarga hasta el dia de ayer.

    gas_updates_df = pd.DataFrame()

    if len(gas_price_to_update) > 0:
        # solo si pasa mas de un dia sin actualizar los datos, en caso contrario, es suficiente con precio_gas_real
        # y gas_updates_df queda vacio.

        # Creation of a dataframe where we are going to concat real price, prev24 and prev48
        gas_updates_df = pd.DataFrame()
        for i in gas_price_to_update.index:
            # Dataframe with the time series
            price_update = pd.DataFrame(
                pd.date_range(
                    gas_price_to_update.loc[i, ["fechaDia"]][0],
                    end=gas_price_to_update.loc[i, ["fechaDia"]][0]
                    + timedelta(days=1),
                    freq="H",
                    tz="Africa/Ceuta",
                )
            )

            price_update = price_update.iloc[:-1, :]

            # column price of the gas
            price_update[FASE1_DATASET["columns_input_v0"]["col_gas"]] = (
                gas_price_to_update.loc[
                    i, [FASE1_DATASET["columns_input_v0"]["col_gas"]]
                ][0]
            )

            # Change the name of the columns
            price_update.columns = [
                FASE1_DATASET["columns_input_v0"]["col_date"],
                FASE1_DATASET["columns_input_v0"]["col_gas"],
            ]

            # Treatment of the date column, eliminating time zone (6 last digits)
            price_update[FASE1_DATASET["columns_input_v0"]["col_date"]] = (
                price_update[
                    FASE1_DATASET["columns_input_v0"]["col_date"]
                ].apply(lambda x: str(x)[:-6])
            )

            # change format of date column
            price_update[FASE1_DATASET["columns_input_v0"]["col_date"]] = (
                price_update[
                    FASE1_DATASET["columns_input_v0"]["col_date"]
                ].apply(lambda x: datetime.strptime(x, date_format))
            )

            gas_updates_df = pd.concat([gas_updates_df, price_update])

        gas_updates_df = gas_updates_df.sort_values(
            by=FASE1_DATASET["columns_input_v0"]["col_date"], ascending=True
        ).reset_index(drop=True)

    try:
        # Merge of the old_dataset (last updated dataset_input_v0) with the new information

        gas_real_price_update = gas_updates_df.merge(
            old_input_gas[
                [
                    FASE1_DATASET["columns_input_v0"]["col_date"],
                    FASE1_DATASET["columns_input_v0"]["col_gas_prev24"],
                    FASE1_DATASET["columns_input_v0"]["col_gas_prev48"],
                ]
            ],
            how="left",
            on=[FASE1_DATASET["columns_input_v0"]["col_date"]],
        )
    except:
        logger1.error("dataset_input_v0 is already updated.")
        raise

    gas_real_price = pd.concat(
        [gas_real_price, gas_real_price_update]
    ).reset_index(drop=True)

    # We proceed with the same logic to input values in prev_24 and prev_48
    # los precios de hoy (today_date) y mañana (today_date +1) son el mismo precio de hoy obtenido desde la web
    gas_price_next_24 = pd.DataFrame(
        pd.date_range(
            today_date,
            end=today_date + timedelta(days=1),
            freq="H",
            tz="Africa/Ceuta",
        )
    ).iloc[:-1, :]

    gas_price_next_24.columns = [FASE1_DATASET["columns_input_v0"]["col_date"]]

    gas_price_next_24[FASE1_DATASET["columns_input_v0"]["col_date"]] = (
        gas_price_next_24[FASE1_DATASET["columns_input_v0"]["col_date"]].apply(
            lambda x: str(x)[:-6]
        )
    )

    gas_price_next_24[FASE1_DATASET["columns_input_v0"]["col_date"]] = (
        gas_price_next_24[FASE1_DATASET["columns_input_v0"]["col_date"]].apply(
            lambda x: datetime.strptime(x, date_format)
        )
    )

    gas_price_next_24 = gas_price_next_24.merge(
        old_input_gas[
            [
                FASE1_DATASET["columns_input_v0"]["col_date"],
                FASE1_DATASET["columns_input_v0"]["col_gas_prev48"],
            ]
        ],
        how="left",
        on=[FASE1_DATASET["columns_input_v0"]["col_date"]],
    )

    gas_price_next_24[FASE1_DATASET["columns_input_v0"]["col_gas_prev24"]] = (
        gas_price_today
    )

    gas_price_next_48 = pd.DataFrame(
        pd.date_range(
            today_date + timedelta(days=1),
            end=today_date + timedelta(days=2),
            freq="H",
            tz="Africa/Ceuta",
        )
    ).iloc[:-1, :]

    gas_price_next_48.columns = [FASE1_DATASET["columns_input_v0"]["col_date"]]

    gas_price_next_48[FASE1_DATASET["columns_input_v0"]["col_gas_prev48"]] = (
        gas_price_tomorrow
        if bool(gas_price_tomorrow) == True
        else gas_price_today
    )

    gas_price_next_48[FASE1_DATASET["columns_input_v0"]["col_date"]] = (
        gas_price_next_48[FASE1_DATASET["columns_input_v0"]["col_date"]].apply(
            lambda x: str(x)[:-6]
        )
    )

    gas_price_next_48[FASE1_DATASET["columns_input_v0"]["col_date"]] = (
        gas_price_next_48[FASE1_DATASET["columns_input_v0"]["col_date"]].apply(
            lambda x: datetime.strptime(x, date_format)
        )
    )
    # update gas

    # Here we input 6 first hours of next day with the same price as previous day,
    # This is done for both prev_24 and prev_48
    gas_price_next_24[
        FASE1_DATASET["columns_input_v0"]["col_gas_prev24"]
    ].iloc[0:6] = (
        gas_real_price[FASE1_DATASET["columns_input_v0"]["col_gas"]]
        .dropna()
        .iloc[-1]
    )
    gas_price_next_48[
        FASE1_DATASET["columns_input_v0"]["col_gas_prev48"]
    ].iloc[0:6] = (
        gas_price_next_24[FASE1_DATASET["columns_input_v0"]["col_gas_prev24"]]
        .dropna()
        .iloc[-1]
    )

    # We concat all the dataframes created following an index based procedure
    gas_update = pd.concat(
        [gas_real_price, gas_price_next_24, gas_price_next_48]
    )

    return gas_update


def get_co2_data(
    date,
    download_path=PATHS["LOCAL"]["download_path"],
):
    """Download historical co2 prices from Sendeco web page and current future price for EUA from The Ice web page

    Parameters
    ----------
    date : str
        date at which updated is requested
    driver_path : str, optional
        path where chrome web driver is located, by default PATHS["LOCAL"]["driver_path"]
    download_path :str, optional
        downloads path, by default PATHS["LOCAL"]["download_path"]

    Returns
    -------
    dictionary
        dictionary with historical Co2 prices and current EUA future price
    """

    date = date + " 00:00:00"
    today_date = datetime.strptime(date, "%Y-%m-%d 00:00:00")
    today_name = today_date.strftime("%A")
    year = str(today_date.year)

    # Delete previous sendeco_dataset

    file_name = FASE1_DATA_SCRAPING["co2_file_name"]
    file_name = os.path.join(download_path, file_name)

    xslx_files = glob.glob(download_path + "/*.csv")

    if file_name in xslx_files:
        os.remove(file_name)

    # Descargar histórico de precios del co2 desde la web de sendeco2

    driver = get_driver()

    driver.get(FASE1_DATA_SCRAPING["url_co2_1"])
    driver.implicitly_wait(3)

    button = driver.find_element(
        by=By.PARTIAL_LINK_TEXT, value="Descargar histórico"
    )
    button.click()
    time.sleep(10)

    co2_price_historical = pd.read_csv(file_name, sep=";", index_col=0)
    co2_price_historical = co2_price_historical.reset_index()

    # Obtener precio del indice de EUA en la web theice
    driver.get(FASE1_DATA_SCRAPING["url_co2_2"])
    driver.implicitly_wait(3)

    td_elements = driver.find_elements(By.TAG_NAME, "td")
    td_elements = [i.text for i in td_elements]
    # eua_index_name = 'DEC22'

    try:
        try:
            co2_date_index = td_elements.index(
                FASE1_DATA_SCRAPING["eua_index_name"]
            )
            logger1.info(
                f"EUA future: {FASE1_DATA_SCRAPING['eua_index_name']}"
            )
        except:
            co2_date_index = td_elements.index(
                FASE1_DATA_SCRAPING[dict_months["12"]]
            )
            logger1.info(f"EUA future: " + dict_months["12"])
    except:
        logger1.warning(
            f"Trying to get {FASE1_DATA_SCRAPING['eua_index_name']}. See The Ice url or change future"
        )

    co2_short_date = td_elements[co2_date_index]
    co2_price = td_elements[co2_date_index + 1]
    co2_full_date = td_elements[co2_date_index + 2]
    find_tag = driver.find_elements(By.TAG_NAME, "td")[6].text
    logger1.info(f"EUA price: {co2_price}")

    try:
        co2_price = float(co2_price)  # precio tomado de the ice
    except:
        logger1.warning(
            "No CO2 price available for today, last price available was taked. See THE ICE url"
        )

    driver.close()

    return {
        "co2_price_historical": co2_price_historical,
        "co2_index_price": co2_price,
    }


def co2_price_update(
    date,
    old_df,
    download_path=PATHS["LOCAL"]["download_path"],
):
    """Update historical Co2 price and forecasts prev24, prev48

    Parameters
    ----------
    date : str
        date at which updated is requested
    old_df : df
        dataset_input_v0 to be updated
    driver_path : str, optional
        path where chrome web driver is located, by default PATHS["LOCAL"]["driver_path"]
    download_path :str, optional
        downloads path, by default PATHS["LOCAL"]["download_path"]

    Returns
    -------
    df
        updated Co2 dataset_input_v0 columns
    """
    date_format = "%Y-%m-%d %H:%M:%S"

    old_input_co2 = old_df[
        [
            FASE1_DATASET["columns_input_v0"]["col_date"],
            FASE1_DATASET["columns_input_v0"]["col_co2"],
            FASE1_DATASET["columns_input_v0"]["col_co2_prev24"],
            FASE1_DATASET["columns_input_v0"]["col_co2_prev48"],
        ]
    ]

    # En el caso del co2 los últimos dos dias de la data, no son el precio real, se deben cambiar los datos del dia d y del d+1
    # (last_day_data y last_day_model_update)
    last_day_data = old_input_co2[
        FASE1_DATASET["columns_input_v0"]["col_date"]
    ][
        len(old_input_co2) - 1
    ]  # ultimo dia en la data-corresponde a un dia posterior a la actualizacion
    last_day_model_update = last_day_data - timedelta(
        days=1
    )  # dia en que se descargaron los datos por ultima vez
    today_date = datetime.strptime(date, "%Y-%m-%d")

    # data con precios reales hasta la ultima actualizacion. En el caso del c02, asi como en el gas,
    # se puede confiar como dato real hasta el dia anterior a la actualizacion de los datos (last_day_model_update-1)
    co2_real_price = old_input_co2.iloc[
        np.where(
            old_input_co2[FASE1_DATASET["columns_input_v0"]["col_date"]]
            <= last_day_model_update - timedelta(days=1)
        )[0],
    ]

    # tener en cuenta que en esios en lugar de actualizar a partir de las 10 del dia anterior, se actualizará todo el dia anterior
    # -----------------------------------------------------------------------------------------------------------------------------
    co2_data = get_co2_data(
        date,
        download_path,
    )  # get data del presente año
    # co2_data = copy.deepcopy(scrap_co2)
    co2_historical_price = co2_data["co2_price_historical"]

    # precio historico del presente año
    if co2_data["co2_index_price"] == "":
        co2_index_price = co2_data["co2_price_historical"][
            FASE1_DATASET["columns_input_v0"]["col_co2"]
        ].values[-1]
    else:
        co2_index_price = co2_data["co2_index_price"]

    # Para los precios historicos, se llenan los campos que no tienen data,
    # como por ejemplo sabados, domingos y festivos, con el ultimo valor disponible

    co2_historical_price["Fecha"] = co2_historical_price["Fecha"].apply(
        lambda x: datetime.strptime(x.replace("/", "-"), "%d-%m-%Y")
    )

    fechas = pd.DataFrame(
        pd.date_range(
            co2_historical_price["Fecha"][0],
            end=today_date,
            freq="D",
        )
    )  # historical price tiene fechas solo para los dias que tiene un valor de co2
    fechas.columns = [
        "Fecha"
    ]  # con fechas se crea un df con todas las fechas disponibles,
    co2_historical_price = fechas.merge(
        co2_historical_price, how="left"
    )  # los campos sin valor de co2 quedan Nan
    last_price_available = co2_historical_price[
        FASE1_DATASET["columns_input_v0"]["col_co2"]
    ][0]
    for i in co2_historical_price.index:
        if (
            np.isnan(
                co2_historical_price[
                    FASE1_DATASET["columns_input_v0"]["col_co2"]
                ][i]
            )
            == False
        ):
            last_price_available = co2_historical_price[
                FASE1_DATASET["columns_input_v0"]["col_co2"]
            ][i]

        else:
            co2_historical_price[FASE1_DATASET["columns_input_v0"]["col_co2"]][
                i
            ] = last_price_available

            logger1.warning("No CO2 data, filling with last available values.")

    co2_historical_price["Fecha"] = co2_historical_price["Fecha"].apply(
        lambda x: x.strftime("%Y-%m-%d")
    )
    co2_historical_price["Fecha"] = co2_historical_price["Fecha"].apply(
        lambda x: datetime.strptime(x, "%Y-%m-%d")
    )

    date_now = str(time.strftime("%Y-%m-%d"))

    if date == date_now:
        co2_index_price = co2_data["co2_index_price"]
    else:
        co2_index_price = co2_historical_price.iloc[
            np.where(co2_historical_price["Fecha"] == date)[0],
        ].reset_index(drop=True)
        co2_index_price = co2_index_price[
            FASE1_DATASET["columns_input_v0"]["col_co2"]
        ][0]

    # Se añaden el precio de hoy y mañana
    # today_date = datetime.strptime(date, '%Y-%m-%d')
    co2_price_df = pd.DataFrame(
        pd.date_range(today_date, end=today_date + timedelta(days=1), freq="D")
    )
    co2_price_df[FASE1_DATASET["columns_input_v0"]["col_co2"]] = (
        co2_index_price
    )
    co2_price_df.columns = [
        "Fecha",
        FASE1_DATASET["columns_input_v0"]["col_co2"],
    ]

    # Como estamos haciendo pruebas es necesario filtrar co2_historical como si sólo tuviera la información relativa hasta el dia anterior
    # a la actualización de los datos (today_date)
    co2_historical = co2_historical_price.iloc[
        np.where(co2_historical_price["Fecha"] < today_date)
    ]

    co2_real_price_to_update = co2_historical.iloc[
        np.where(
            (
                co2_historical["Fecha"]
                >= last_day_model_update - timedelta(days=1)
            )
        )
    ]

    # Se actualizan los precios para los dias desde la ultima descarga hasta el dia d+1.

    def insert_day_values(df):
        co2_updates_df = pd.DataFrame()
        for i in df.index:
            price_update = pd.DataFrame(
                pd.date_range(
                    df.loc[i, ["Fecha"]][0],
                    end=df.loc[i, ["Fecha"]][0] + timedelta(days=1),
                    freq="H",
                    tz="Africa/Ceuta",
                )
            )
            price_update = price_update.iloc[:-1, :]
            price_update[FASE1_DATASET["columns_input_v0"]["col_co2"]] = (
                df.loc[i, [FASE1_DATASET["columns_input_v0"]["col_co2"]]][0]
            )
            price_update.columns = [
                FASE1_DATASET["columns_input_v0"]["col_date"],
                FASE1_DATASET["columns_input_v0"]["col_co2"],
            ]
            price_update[FASE1_DATASET["columns_input_v0"]["col_date"]] = (
                price_update[
                    FASE1_DATASET["columns_input_v0"]["col_date"]
                ].apply(lambda x: str(x)[:-6])
            )
            price_update[FASE1_DATASET["columns_input_v0"]["col_date"]] = (
                price_update[
                    FASE1_DATASET["columns_input_v0"]["col_date"]
                ].apply(lambda x: datetime.strptime(x, date_format))
            )
            co2_updates_df = pd.concat([co2_updates_df, price_update])
        co2_updates_df = co2_updates_df.sort_values(
            by=FASE1_DATASET["columns_input_v0"]["col_date"], ascending=True
        ).reset_index(drop=True)

        return co2_updates_df

    co2_real_price_update = insert_day_values(co2_real_price_to_update)
    co2_real_price_update = co2_real_price_update.merge(
        old_input_co2[
            [
                FASE1_DATASET["columns_input_v0"]["col_date"],
                FASE1_DATASET["columns_input_v0"]["col_co2_prev24"],
                FASE1_DATASET["columns_input_v0"]["col_co2_prev48"],
            ]
        ],
        how="left",
        on=[FASE1_DATASET["columns_input_v0"]["col_date"]],
    )
    co2_real_price = pd.concat(
        [co2_real_price, co2_real_price_update]
    ).reset_index(drop=True)

    co2_prev24 = insert_day_values(co2_price_df.iloc[:1, :])
    co2_prev24.columns = [
        FASE1_DATASET["columns_input_v0"]["col_date"],
        FASE1_DATASET["columns_input_v0"]["col_co2_prev24"],
    ]
    co2_prev24 = co2_prev24.merge(
        old_input_co2[
            [
                FASE1_DATASET["columns_input_v0"]["col_date"],
                FASE1_DATASET["columns_input_v0"]["col_co2_prev48"],
            ]
        ],
        how="left",
        on=[FASE1_DATASET["columns_input_v0"]["col_date"]],
    )

    co2_prev48 = insert_day_values(co2_price_df.iloc[1:, :])
    co2_prev48.columns = [
        FASE1_DATASET["columns_input_v0"]["col_date"],
        FASE1_DATASET["columns_input_v0"]["col_co2_prev48"],
    ]

    # update co2
    new_inputs = [co2_real_price, co2_prev24, co2_prev48]
    co2_update = reduce(
        lambda left, right: pd.merge(
            left,
            right,
            on=[FASE1_DATASET["columns_input_v0"]["col_date"]],
            how="outer",
        ),
        new_inputs,
    )

    prev24_x = co2_update[
        [FASE1_DATASET["columns_input_v0"]["col_date"], "EUA_prev24_x"]
    ].iloc[
        np.where(
            co2_update[FASE1_DATASET["columns_input_v0"]["col_date"]]
            < co2_prev24[FASE1_DATASET["columns_input_v0"]["col_date"]].values[
                0
            ]
        )[0]
    ]
    prev24_y = co2_update[
        [FASE1_DATASET["columns_input_v0"]["col_date"], "EUA_prev24_y"]
    ].iloc[
        np.where(
            co2_update[FASE1_DATASET["columns_input_v0"]["col_date"]]
            >= co2_prev24[
                FASE1_DATASET["columns_input_v0"]["col_date"]
            ].values[0]
        )[0]
    ]
    co2_update[FASE1_DATASET["columns_input_v0"]["col_co2_prev24"]] = (
        pd.concat([prev24_x["EUA_prev24_x"], prev24_y["EUA_prev24_y"]])
    )

    prev48_x = co2_update[
        [FASE1_DATASET["columns_input_v0"]["col_date"], "EUA_prev48_x"]
    ].iloc[
        np.where(
            co2_update[FASE1_DATASET["columns_input_v0"]["col_date"]]
            < co2_prev24[FASE1_DATASET["columns_input_v0"]["col_date"]].values[
                0
            ]
        )[0]
    ]
    prev48_y = co2_update[
        [FASE1_DATASET["columns_input_v0"]["col_date"], "EUA_prev48_y"]
    ].iloc[
        np.where(
            (
                co2_update[FASE1_DATASET["columns_input_v0"]["col_date"]]
                >= co2_prev24[
                    FASE1_DATASET["columns_input_v0"]["col_date"]
                ].values[0]
            )
            & (
                co2_update[FASE1_DATASET["columns_input_v0"]["col_date"]]
                < co2_prev48[
                    FASE1_DATASET["columns_input_v0"]["col_date"]
                ].values[0]
            )
        )[0]
    ]
    prev48_z = co2_update[
        [
            FASE1_DATASET["columns_input_v0"]["col_date"],
            FASE1_DATASET["columns_input_v0"]["col_co2_prev48"],
        ]
    ].iloc[
        np.where(
            co2_update[FASE1_DATASET["columns_input_v0"]["col_date"]]
            >= co2_prev48[
                FASE1_DATASET["columns_input_v0"]["col_date"]
            ].values[0]
        )[0]
    ]

    co2_update[FASE1_DATASET["columns_input_v0"]["col_co2_prev48"]] = (
        pd.concat(
            [
                prev48_x["EUA_prev48_x"],
                prev48_y["EUA_prev48_y"],
                prev48_z[FASE1_DATASET["columns_input_v0"]["col_co2_prev48"]],
            ]
        )
    )

    co2_update = co2_update.drop(
        columns=[
            "EUA_prev24_x",
            "EUA_prev48_x",
            "EUA_prev24_y",
            "EUA_prev48_y",
        ]
    )
    co2_update = co2_update[
        [
            FASE1_DATASET["columns_input_v0"]["col_date"],
            FASE1_DATASET["columns_input_v0"]["col_co2"],
            FASE1_DATASET["columns_input_v0"]["col_co2_prev24"],
            FASE1_DATASET["columns_input_v0"]["col_co2_prev48"],
        ]
    ]

    return co2_update
