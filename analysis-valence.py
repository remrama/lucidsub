"""
export just the stats and values after comparing frequency of only-neg and only-post posts
"""
import os
import json
import pandas as pd
import pingouin as pg
import config as c

from statsmodels.stats.proportion import proportions_ztest

import_fname = os.path.join(c.RESULTS_DIR, "themes-highlights_table.csv")
export_fname = os.path.join(c.RESULTS_DIR, "valence.json")

# all this junk gets down to only the posts with just neg
# or just pos themes (doesn't care how many themes within pos or neg)
ser = pd.read_csv(import_fname, usecols=[0,1],
        index_col="post_id", squeeze=True
    ).replace(c.POS_THEMES, True
    ).replace(c.NEG_THEMES, False
    ).rename("positive"
    ).reset_index(
        ).drop_duplicates(subset=None, # drop duplicated pos or neg within post
        ).drop_duplicates(subset="post_id", keep=False # drop all posts with pos and neg
        ).set_index("post_id"
        ).squeeze()


n_pos = ser.value_counts().loc[True]
n_neg = ser.value_counts().loc[False]
n_obs = ser.size
assert n_obs == n_pos+n_neg

zstat, pval = proportions_ztest(count=n_pos, nobs=n_obs,
    value=.5, alternative="two-sided")


stats_out = {
    "n_observed": n_obs,
    "n_positive": int(n_pos), # wrapped in int for json, numpy ints don't work
    "n_negative": int(n_neg),
    "z": round(zstat, 5),
    "p": round(pval, 5)
}


with open(export_fname, "wt", encoding="utf-8") as f:
    json.dump(stats_out, f, indent=4, ensure_ascii=True)
