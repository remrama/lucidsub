"""Compare positive and negative theme popularity statistically.
"""
import os
import pandas as pd
import pingouin as pg
import utils

import matplotlib.pyplot as plt
utils.load_matplotlib_settings()


import_basename = "themes-descriptives.csv"
export_basename = "themes-popularity_stats.csv"
import_fullpath = os.path.join(utils.Config.data_directory, "results", import_basename)
export_fullpath = import_fullpath.replace(import_basename, export_basename)


# Get positive and negative theme names.
pos_themes = sorted(utils.Config.themes.positive)
neg_themes = sorted(utils.Config.themes.negative)

# Load data.
df = pd.read_csv(import_fullpath, index_col="theme")

# Extract data for analysis.
df = df[:-2] # remove pos/neg summary scores
pos_upvotes = df.loc[pos_themes, "score-median"].tolist()
pos_comments = df.loc[pos_themes, "n-comments-median"].tolist()
neg_upvotes = df.loc[neg_themes, "score-median"].tolist()
neg_comments = df.loc[neg_themes, "n-comments-median"].tolist()

# Get descriptive statistics.
pos_descr = df.loc[pos_themes, ["score-median", "n-comments-median"]].agg(["count", "mean", "median", "std"]).round(1)
neg_descr = df.loc[neg_themes, ["score-median", "n-comments-median"]].agg(["count", "mean", "median", "std"]).round(1)

# Run statistics.
upvote_stats = pg.mwu(pos_upvotes, neg_upvotes)
comment_stats = pg.mwu(pos_comments, neg_comments)

# Wrangle into one dataframe.
upvote_stats.columns = upvote_stats.columns.map(lambda x: f"MWU-{x}")
comment_stats.columns = comment_stats.columns.map(lambda x: f"MWU-{x}")
stats = pd.concat([upvote_stats, comment_stats]).T
pos_descr.columns = ["upvotes", "comments"]
neg_descr.columns = ["upvotes", "comments"]
pos_descr.index = pos_descr.index.map(lambda x: f"neg-{x}")
neg_descr.index = neg_descr.index.map(lambda x: f"pos-{x}")
stats.columns = ["upvotes", "comments"]
summary = pd.concat([stats, pos_descr, neg_descr])


# Export
summary.to_csv(export_fullpath, index_label="statistic")
