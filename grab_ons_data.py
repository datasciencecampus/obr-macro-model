from pathlib import Path

import pandas as pd
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
        try:
            data = requests.get(ROOT_URL + f"timeseries/{series_id}").json()
            dataset_id = data["items"][0]["description"]["datasetId"]
            temp_df = pd.DataFrame.from_dict(
                {"series_id": series_id, "dataset_id": dataset_id}, orient="index"
            ).T
            series_dataset_df = pd.concat([series_dataset_df, temp_df])
        except:
            logger.debug(f"Was not able to retrieve series id {series_id}")
    logger.info(
        f"Dataset ids for {len(series_dataset_df)} time series have been downloaded out of a possible {len(series_identifiers)}."
    )
    # every row is numbered '0', so give rows distinct numbers
    series_dataset_df = series_dataset_df.reset_index(drop=True)
    return series_dataset_df


def get_an_ONS_time_series(dataset_id: str, timeseries_id: str) -> pd.DataFrame:
    """Get dataframe of time series based on dataset and timeseries IDs.

    Example:
    >>> data = get_an_ONS_time_series("PN2", "ABJR")

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
    data_df["timeseries_id"] = timeseries_id
    data_df["dataset_id"] = dataset_id
    return data_df


# programme logic:
# get all series ids in the model, get all dataset ids
# then get all data from those series and dataset ids
# then clean and store
series_ids_for_model = get_list_of_model_series_identifiers()
datasets_df = get_series_ids_and_datasets(series_ids_for_model)
# now we need to run through the available series IDs & download data
df = pd.DataFrame()
for row_num, row in datasets_df.iterrows():
    try:
        this_data_frame = get_an_ONS_time_series(row["dataset_id"], row["series_id"])
        df = pd.concat([df, this_data_frame])
    except:
        logger.debug(
            f"Was not able to retrieve series {row['series_id']} from dataset {row['dataset_id']}."
        )

# clean up dataframe typing
typing_dict = {
    "date": "category",
    "label": "category",
    "quarter": "category",
    "source_dataset": "category",
    "timeseries_id": "category",
    "dataset_id": "category",
    "month": "category",
    "update_date": "datetime64[ns]",
    "datetime": "datetime64[ns]",
    "year": "int",
    "title": "string",
    "value": "double",
}
# some whitespace strings in value, so this is needed
df["value"] = pd.to_numeric(df["value"])
df = df.astype(typing_dict)
df.to_parquet(Path("data/model_series/model_series_long.parquet"))
