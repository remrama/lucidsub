"""Compare the frequencies of *only* negative and *only* positive posts.
Export their total counts and the statistics in one table.

ALSO export a few files for later use/convenience.
    1. A jsonl file of the pos/neg-only posts, for the second Doccano analysis.
    2. A json file listing all the IDs of pos/neg-only posts, to extract from the larger corpus later.
"""
import os
import json
import pandas as pd
import utils

from statsmodels.stats.proportion import proportions_ztest


# I/O
export_basename = "themes-valence.csv"
export_basename_json = export_basename.replace(".csv", ".json")
export_basename_jsonl = export_basename.replace(".csv", ".jsonl")
export_fullpath = os.path.join(utils.Config.data_directory, "results", export_basename)
export_fullpath_json = os.path.join(utils.Config.data_directory, "derivatives", export_basename_json)
export_fullpath_jsonl = os.path.join(utils.Config.data_directory, "derivatives", export_basename_jsonl)

import_basename_raw = f"r-LucidDreaming_{utils.Config.scrape_timestamp}.csv"
import_fullpath_raw = os.path.join(utils.Config.data_directory, "source", import_basename_raw)


# Load the full/final dataset of themes for each post.
df = utils.load_final_post_themes(utils.Config)
# and set themes as index.
df = df.T

# Reduce theme names to just the valence (ie, positive or negative).
def name2valence(theme):
    if theme in utils.Config.themes.positive:
        return "positive"
    elif theme in utils.Config.themes.negative:
        return "negative"
    else:
        raise ValueError(f"Unexpected theme name: {theme}")
df.index = df.index.map(name2valence).rename("valence")

# Get all positive and negative posts IDs.
positive_posts = df.loc["positive"].any().rename("positive").to_frame().query("positive==True").index.tolist()
negative_posts = df.loc["negative"].any().rename("negative").to_frame().query("negative==True").index.tolist()

# Reduce to only positive and only negative.
positive_only_posts = set(positive_posts) - set(negative_posts)
negative_only_posts = set(negative_posts) - set(positive_posts)

# Count within each group.
n_positive_only_posts = len(positive_only_posts)
n_negative_only_posts = len(negative_only_posts)
n_observations = n_positive_only_posts + n_negative_only_posts

# Run stats.
zstat, pval = proportions_ztest(count=n_positive_only_posts,
    nobs=n_observations, value=.5, alternative="two-sided")

# Insert into a pandas series.
results = {
    "n-observations": n_observations,
    "n-positive-only": n_positive_only_posts,
    "n-negative-only": n_negative_only_posts,
    "z-val": zstat,
    "p-val": pval,
}
series = pd.Series(results, name="value")

# Export.
series.to_csv(export_fullpath, index_label="statistic", encoding="utf-8")


######################################## json file for later

posneg_only_dict = dict(
    positive_only_posts=sorted(list((positive_only_posts))),
    negative_only_posts=sorted(list(negative_only_posts)),
)

# Export for later use (useful to extract these posts out in other scripts).
with open(export_fullpath_json, "w", encoding="utf-8") as json_outfile:
    json.dump(posneg_only_dict, json_outfile, indent=4, ensure_ascii=False)


######################################## jsonl file for Doccano (also later)

# Identify all posts with either only positive or only negative theme(s).
all_only_posts = positive_only_posts.union(negative_only_posts)
assert len(all_only_posts) == len(positive_only_posts) + len(negative_only_posts)

# Load full originally scraped Reddit data.
raw_df = pd.read_csv(import_fullpath_raw, encoding="utf-8", low_memory=False)

# Subset only those posts.
raw_df = raw_df[raw_df["id"].isin(all_only_posts)]

# Mix them up.
raw_df = raw_df.sample(frac=1, random_state=1)

# Export as a jsonl file, for Doccano.
with open(export_fullpath_jsonl, "w", encoding="utf-8") as jsonl_outfile:
    # loop over each row and export with a line between title and text
    for _, row in raw_df.iterrows():
        post_id = row["id"]
        title = row["title"]
        report = row["selftext"]
        title_and_report = "\n::-------------::\n\n".join([title, report])
        data = {
            "text" : title_and_report,
            "id" : post_id,
            "label" : [], # include for doccano
        }
        json.dump(data, jsonl_outfile, ensure_ascii=False)
        jsonl_outfile.write("\n")
