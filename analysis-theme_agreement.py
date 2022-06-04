"""Interrater reliability for themes.

Note that the total number of posts here (213) is more
than the final because some posts with disagreement
did not make the final cut after discussing them.
"""
import os
import numpy as np
import pandas as pd

import utils


N_RATERS = 3

export_basename = "themes-agreement.csv"
import_basename1 = "doccano-postXtheme_2019April.csv"
import_basename2 = "doccano-postXtheme_2019July.csv"
import_fullpath1 = os.path.join(utils.Config.data_directory, "derivatives", import_basename1)
import_fullpath2 = import_fullpath1.replace(import_basename1, import_basename2)
export_fullpath = os.path.join(utils.Config.data_directory, "results", export_basename)

# Load and manipulate data.
df1 = pd.read_csv(import_fullpath1, index_col="post_id")
df2 = pd.read_csv(import_fullpath2, index_col="post_id")
df = pd.concat([df1, df2], axis=0)

# Get percent agreement.
pct_agreement = df.apply(lambda row: row.isin([0, N_RATERS]).mean()
    ).mul(100).rename("pct_agreement").rename_axis("theme")

# Export.
pct_agreement.to_csv(export_fullpath, float_format="%.0f")