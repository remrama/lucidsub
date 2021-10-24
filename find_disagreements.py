"""
save out a csv with JUST the posts with disagreement.
add the text too so we can talk them out.
"""
import os
import argparse
import pandas as pd

import config as c

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--version", type=int, required=True, choices=[1, 2])
args = parser.parse_args()

version = args.version
month = c.MONTHS[f"v{version}"]

import_fname1 = os.path.join(c.RESULTS_DIR, f"doccano-postXtheme_v{version}.csv")
import_fname2 = os.path.join(c.DATA_DIR, f"r-LucidDreaming_2019{month}+200.csv")


export_fname = os.path.join(c.RESULTS_DIR, f"doccano-disagreements2solve_v{version}.csv")

df1 = pd.read_csv(import_fname1, index_col="post_id")
df2 = pd.read_csv(import_fname2)

n_coders = len(c.CODERS)

# select only the post/theme combos with a middle amount of "votes" or coder selections
ser = df1.rename_axis(columns="theme").unstack().rename("n_votes")

subser = ser[(ser>0) & (ser<n_coders)]
subdf = subser.swaplevel().sort_index().reset_index(drop=False)

outdf = pd.merge(subdf, df2[["id", "title", "selftext"]],
    left_on="post_id", right_on="id", validate="m:1")

# outdf["post"] = outdf.apply(lambda row: row["title"]+"\n\n"+row["selftext"], axis=1)
# outdf.drop(columns=["title", "selftext"], inplace=True)

outdf.to_csv(export_fname, index=False)
