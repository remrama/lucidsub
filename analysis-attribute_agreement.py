"""Interrater reliability for attribute ratings (i.e., control and lucidity).

Note, here looking at the two months simultaneously
and loading from raw doccano output.
"""
import os
import string
import numpy as np
import pandas as pd

import utils


ATTRIBUTES = ["lucidity", "control"]
coders = utils.Config.coders[1:]


############ I/O

export_basename = "attributes-agreement.csv"
export_fullpath = os.path.join(utils.Config.data_directory, "results", export_basename)
source_dir = os.path.join(utils.Config.data_directory, "source")


############ Load and wrangle data.

# Load the Doccano ratings/results files.
ser_list = []
for attr in ATTRIBUTES:
    for i, c in enumerate(coders):
        unique_coder_id = string.ascii_uppercase[i]
        import_fname = os.path.join(source_dir, f"doccano-{attr}", f"{c}.csv")
        ser = pd.read_csv(import_fname, usecols=[0,2], index_col="id", squeeze=True).rename_axis("post_id")
        ser = pd.concat({unique_coder_id: ser}, names=["coder"]) # add index level for coder
        ser = pd.concat({attr: ser}, names=["attribute"]) # add index level for attribute
        ser_list.append(ser)

df = pd.concat(ser_list, axis=0).unstack().T

# Adjust the Doccano ratings.
replacements = {
    "lucidity": {"LD": 1, "not an LD": 0},
    "control": {"yes control": 1, "no control": 0, "not a dream": np.nan},
}
df["lucidity"] = df["lucidity"].replace(replacements["lucidity"])
df["control"] = df["control"].replace(replacements["control"])

# Percent agreement.
lucidity_agreement = df["lucidity"]["A"].eq(df["lucidity"]["B"]).mean()
control_agreement = df["control"]["A"].fillna(99).eq(df["control"]["B"].fillna(99)).mean()
pct_agreement = pd.DataFrame.from_dict({
            "lucidity": lucidity_agreement,
            "control": control_agreement,
        }, orient="index"
    ).mul(100
    ).squeeze().rename("pct_agreement")

# Export.
pct_agreement.to_csv(export_fullpath, index_label="attribute", float_format="%.0f")