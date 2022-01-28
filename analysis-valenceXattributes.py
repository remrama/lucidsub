"""Run chi2 analysis on the two extra attribute ratings (lucidity and control)
Export a stats table and a frequency table,
holding results for both analyses in each.
"""
import os
import json
import pandas as pd
import pingouin as pg

import utils


############ I/O

export_basename_freqs = "themes-valenceXattribute_freqs.csv"
export_fullpath_freqs = os.path.join(utils.Config.data_directory, "results", export_basename_freqs)
export_fullpath_stats = export_fullpath_freqs.replace("_freqs", "_stats")

# the list of relevant post IDs
import_fullpath_posts = os.path.join(utils.Config.data_directory, "derivatives", "themes-valence.json")


############ Load and wrangle data.

# Identify the positive- and negative-only posts.
# (note there are more posts from Doccano that don't fit the "only" restriction, so extra important to reduce here)
with open(import_fullpath_posts, "r", encoding="utf-8") as infile:
    post_ids = json.load(infile)

# Turn it into a series with post_id as index.
list_of_lists = [ [(x,k) for x in v] for k, v in post_ids.items() ]
flat_list = [ item for sublist in list_of_lists for item in sublist ]
posts = pd.Series(dict(flat_list), name="valence"
    ).rename_axis("post_id").map(lambda x: x.split("_")[0])



############ Loop over attributes, getting results for each.

freq_results_list = []
stat_results_list = []

for attr in ["control", "lucidity"]:

    # Load the Doccano ratings/results file.
    import_fullpath_ratings = os.path.join(utils.Config.data_directory, "source",
        f"doccano-{attr}", "lsowin.csv")
    ratings = pd.read_csv(import_fullpath_ratings, usecols=[0,2], index_col="id", squeeze=True)

    # Adjust the Doccano ratings.
    if attr == "control":
        replacements = {"yes control": True, "no control": False, "not a dream": pd.NA}
    elif attr == "lucidity":
        replacements = {"LD": True, "not an LD": False}
    ratings = ratings.replace(replacements
        ).rename(attr).rename_axis("post_id"
        ).dropna().astype(bool)

    # Merge the ratings with post valence.
    df = pd.merge(posts, ratings, on="post_id", how="inner", validate="1:1")


    ############ Run stats.
    expected, observed, stats = pg.chi2_independence(df,
        x="valence", y=attr, correction=False)

    # Rearrange results so they're stackable into one file.
    stats.index = pd.Index([attr]*len(stats), name="attribute")
    exp = expected.reset_index().melt(value_name="expected", var_name="present", id_vars="valence")
    exp.index = pd.Index([attr]*4, name="attribute")
    obs = observed.reset_index().melt(value_name="observed", var_name="present", id_vars="valence")
    obs.index = pd.Index([attr]*4, name="attribute")
    freqs = pd.concat([exp.round(1), obs["observed"]], axis=1)

    # Append to lists for exporting together.
    freq_results_list.append(freqs)
    stat_results_list.append(stats)


# Concatenat and export.
freq_results = pd.concat(freq_results_list, axis=0)
stat_results = pd.concat(stat_results_list, axis=0)
freq_results.to_csv(export_fullpath_freqs)
stat_results.to_csv(export_fullpath_stats)
