import pandas as pd
from pathlib import Path
import re
from skimpy import clean_columns

df = pd.read_excel(Path("data/obr/List-of-model-variables_May-2021.xlsx"))

df = (
    df.rename(columns=df.iloc[4])
    .iloc[5:, :]  # drop first few rows before data start
    .assign(group=pd.NA)  # create empty col for group
)
# at every location that's not a number, copy across the value to the group column
df.loc[df["Number"].str.match("\d+\+.*") == False, "group"] = df.loc[
    df["Number"].str.match("\d+\+.*") == False, "Number"
]
df["group"] = df["group"].fillna(method="ffill", axis=0)  # fill group column with this

# nice column names
df = clean_columns(df)

# drop the rows for which number fails above test
df = df.loc[df["number"].str.match("\d+\+.*") != False, :]

# turn every entry in ONS identifier code into a list (regardless of how it appears)
df["list_ons_identifiers"] = (
    df["ons_identifier_code"]
    .apply(lambda x: re.findall("([A-Za-z]{4})", str(x)))
    .values.tolist()
)
clean_list_ons_identifiers = [
    item for sublist in df["list_ons_identifiers"].values for item in sublist
]
# write the clean list of identifiers to file:
with open(Path("data/model_spec/ons_identifiers.txt"), "w") as fp:
    fp.write("\n".join(clean_list_ons_identifiers))

# clean up the model specification spreadsheet:
data_type_dict = {
    "number": "int",
    "variable": "string",
    "model_identifier": "string",
    "ons_identifier_code": "string",
    "equation": "string",
    "equation_type": "string",
    "group": "category",
}
df = df.astype(data_type_dict)
df.to_csv(Path("data/model_spec/model_spec.csv"), index=False)
