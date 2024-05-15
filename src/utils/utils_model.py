"""
    Utils File for PoC Bidding Energia: modelling functions
    Last version May 2022
"""

import os
import sys
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Access files in different directories (only during execution)
basepath = os.path.dirname(__file__)  # script directory
sys.path.insert(1, os.path.join(basepath, "../"))  # add root directory

from config.config_file import *


def split_train_val_test(data, validation_days=14, test_days=7):
    """TS separation into train, validation and test

    Parameters
    ----------
    data : dataFrame
        df to be used in the model
    validation_days : int
        number of days of the validation period
    test_days : int
        number of days of the validation period
    Returns
    -------
    3 TS:
        datos_test: x days test (recommended 1 day)
        datos_val: x days validation (recommended 28 days)
        datos_train: rest of TS

    """
    last_day = str(data.index[-1])

    # if '+01:00' in last_day:
    #    last_day = last_day.replace('+01:00', '')
    # else:
    #    last_day = last_day.replace('+02:00', '')

    end_validation = str(
        datetime.strptime(last_day, "%Y-%m-%d %H:%M:%S") - timedelta(test_days)
    )

    end_validation_1 = str(
        datetime.strptime(last_day, "%Y-%m-%d %H:%M:%S")
        - timedelta(test_days)
        + timedelta(hours=1)
    )

    end_train = str(
        datetime.strptime(end_validation, "%Y-%m-%d %H:%M:%S")
        - timedelta(validation_days)
    )

    end_train_1 = str(
        datetime.strptime(end_validation, "%Y-%m-%d %H:%M:%S")
        - timedelta(validation_days)
        + timedelta(hours=1)
    )

    data_train = data.loc[:end_train, :]
    data_val = data.loc[end_train_1:end_validation, :]
    data_test = data.loc[end_validation_1:, :]

    print(
        f"Train dates      : {data_train.index.min()} --- {data_train.index.max()}  (n hours={len(data_train)})"
    )
    print(
        f"Validation dates : {data_val.index.min()} --- {data_val.index.max()}  (n hours={len(data_val)})"
    )
    print(
        f"Test date       : {data_test.index.min()} --- {data_test.index.max()}  (n hours={len(data_test)})"
    )

    return data_train, data_val, data_test, end_validation, end_validation_1
