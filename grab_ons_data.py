import pandas as pd
from pathlib import Path
import requests
from loguru import logger
from skimpy import clean_columns


ROOT_URL = "https://api.beta.ons.gov.uk/"


def get_list_of_model_series_identifiers() -> list:
    """Retrieve four letter ONS codes from an OBR model specification.

    Returns:
        list: The list of four letter codes (capitalised).
    """
    with open(Path("data/model_spec/ons_identifiers.txt")) as f:
        lines = [x.strip("\n") for x in f.readlines()]
    unique_list = list(set(lines))
    logger.info(
        f"There are {len(unique_list)} unique ONS time series codes in the model."
    )
    return unique_list


def get_series_ids_and_datasets(series_identifiers: list) -> pd.DataFrame:
    """Match up a given list of series identifiers with their dataset IDs.

    Args:
        series_identifiers (list): list of four letter ONS codes (capitalised)

    Returns:
        pd.DataFrame: Dataframe with ONS series and dataset columns
    """
    series_dataset_df = pd.DataFrame()
    for series_id in series_identifiers:
        data = requests.get(ROOT_URL + f"timeseries/{series_id}").json()
        dataset_id = data["items"][0]["description"]["datasetId"]
        temp_df = pd.DataFrame.from_dict(
            {"series_id": series_id, "dataset_id": dataset_id}, orient="index"
        ).T
        series_dataset_df = pd.concat([series_dataset_df, temp_df])
    logger.info(
        f"Dataset ids for {len(series_dataset_df)} time series have been downloaded."
    )
    return series_dataset_df


def get_an_ONS_time_series(dataset_id: str, timeseries_id: str) -> pd.DataFrame:
    """Get dataframe of time series based on dataset and timeseries IDs.

    Args:
        dataset_id (str): ONS dataset ID, eg PN2
        timeseries_id (str): ONS timeseries ID, eg ABJR

    Returns:
        pd.DataFrame: _description_
    """
    # This function grabs specified time series from the ONS API.
    api_endpoint = "https://api.ons.gov.uk/"
    api_params = {"dataset": dataset_id, "timeseries": timeseries_id}
    url = (
        api_endpoint
        + "/".join(
            [x + "/" + y for x, y in zip(api_params.keys(), api_params.values())][::-1]
        )
        + "/data"
    )
    data = requests.get(url).json()
    title = data["description"]["title"]
    # check if monthly or quarterly from whichever list not empty
    if data["months"] != []:
        time_series_data = data["months"]
    else:
        time_series_data = data["quarters"]
    data_df = pd.DataFrame(pd.json_normalize(time_series_data))
    data_df["title"] = title
    logger.debug("Quarter-only hard-coded here")
    data_df["date_string"] = data_df["year"] + "-" + data_df["quarter"]
    data_df["datetime"] = pd.to_datetime(data_df["date_string"])
    data_df = clean_columns(data_df)
    return data_df


# example use
data = get_an_ONS_time_series("PN2", "ABJR")
