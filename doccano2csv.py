"""Load in the Doccano codings/output and generate 3 csv files
that highlight themes (dis)agreeance among coders.

They're tables to be plotted in other scripts.

1. postXtheme, n coders per post that selected each theme
2. postXthemeXcoder, same as above, but broken down by coder
3. disagreements, JUST the posts with disagreement, for viewing

+++ Note that even though coders selected specific
    *sections* of each post as part of a theme or not,
    we're only interested in binary yes/no did a post
    have any of a subtheme or not. So only that information
    is going from Doccano to these output files.
"""
import os
import json
import string
import argparse
import pandas as pd

import utils


parser = argparse.ArgumentParser()
parser.add_argument("-m", "--month", type=str, required=True, help="Month is needed to load/export proper filenames now")
args = parser.parse_args()


MONTH_STR = args.month
month_cap = MONTH_STR.capitalize()


all_themes = utils.Config.themes.positive + utils.Config.themes.negative


### Load in the original Reddit posts, for the extra info that wasn't initially exported.
### Other than that, loading in the Doccano ratings.
import_fname_reddit = os.path.join(utils.Config.data_directory, "derivatives", f"r-LucidDreaming_2019{month_cap}+200.csv")
doccano_directory = os.path.join(utils.Config.data_directory, "source", f"doccano-2019{month_cap}")

export_bname1 = f"doccano-postXtheme_2019{month_cap}.csv"
export_bname2 = f"doccano-postXthemeXcoder_2019{month_cap}.csv"
export_bname3 = f"doccano-disagreements_2019{month_cap}.csv"
export_fname1 = os.path.join(utils.Config.data_directory, "derivatives", export_bname1)
export_fname2 = os.path.join(utils.Config.data_directory, "derivatives", export_bname2)
export_fname3 = os.path.join(utils.Config.data_directory, "derivatives", export_bname3)


# Load in Doccano data.
data = {}
for i, c in enumerate(utils.Config.coders):
    unique_coder_id = string.ascii_uppercase[i]
    import_fname = os.path.join(doccano_directory, f"{c}.jsonl")
    with open(import_fname, "r", encoding="utf-8") as infile:
        coder_data = [ json.loads(l) for l in infile.read().splitlines() ]
    # convert from list to a dict that has post id as keys and labels
    coder_data = { post["id"] : post["label"] for post in coder_data }
    data[unique_coder_id] = coder_data

# Convert Doccano data to a dataframe with one SECTION/label
# per row and coder/post_id/subtheme as columns
# (so each post has multiple rows).
row_list = []
for coder, coder_data in data.items():
    for post_id, coded_section in coder_data.items():
        for start, end, subtheme in coded_section:
            # correct original mislabeling of theme in doccano
            subtheme = "Lucid dysphoria" if subtheme == "Lucid nightmares" else subtheme
            subtheme = "Positive waking mood" if subtheme == "Positive morning mood" else subtheme
            if subtheme in all_themes:
                df_row = dict(coder=coder, post_id=post_id, subtheme=subtheme)
                row_list.append(df_row)

df = pd.DataFrame(row_list)

# Drop duplicates bc sometimes the same theme is there >1 in a single post.
df.drop_duplicates(inplace=True, ignore_index=True)


# Wrangle into desired structures.

postXtheme = df.groupby("post_id")["subtheme"
    ].value_counts(dropna=False).unstack(fill_value=0
    ).reindex(columns=all_themes, fill_value=0)

postXthemeXcoder = df.groupby(["subtheme","coder"]
    )["post_id"].value_counts(dropna=False
    ).unstack(fill_value=0
    ).reindex(
        pd.MultiIndex.from_product([all_themes, data.keys()], names=["subtheme", "coder"]),
        axis="index", fill_value=0)


# Export agreement frequency csv files.
postXtheme.to_csv(export_fname1, index=True)
postXthemeXcoder.to_csv(export_fname2, index=True)


############## Build the disagreements file.
# Merge the postXtheme file with the original/cleaned Reddit data.

df1 = postXtheme.reset_index(drop=False).set_index("post_id")
df2 = pd.read_csv(import_fname_reddit, encoding="utf-8") # Reddit data

n_coders = len(utils.Config.coders)

# Select only the post/theme combos with a middle amount of "votes" or coder selections.
ser = df1.rename_axis(columns="theme").unstack().rename("n_votes")

subser = ser[(ser>0) & (ser<n_coders)]
subdf = subser.swaplevel().sort_index().reset_index(drop=False)

outdf = pd.merge(subdf, df2[["id", "title", "selftext"]],
    left_on="post_id", right_on="id", validate="m:1")

outdf.to_csv(export_fname3, index=False)
