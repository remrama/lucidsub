"""Want to export a csv file that shows
disagreements (for each theme) so that
they can be found easily for discussion.

Also export a table and plot showing the disagreement at that time.

Load in the Doccano output and generate a few csv files.

+++ Note that even though coders selected specific
    *sections* of each post as part of a theme or not,
    we're only interested in binary yes/no did a post
    have any of a subtheme or not. So that information
    is getting from doccano to these output files.
"""
import os
import json
import string
import pandas as pd

import config as c


# could just glob this
CODERS = ["remym", "lsowin", "rraider"]

all_themes = c.POS_THEMES + c.NEG_THEMES

doccano_dir = os.path.join(c.DATA_DIR, "doccano-20210822")

export_fname1 = os.path.join(c.RESULTS_DIR, "doccano-postXtheme.csv")
export_fname2 = os.path.join(c.RESULTS_DIR, "doccano-postXthemeXcoder.csv")

# load in doccano data
data = {}
for i, c in enumerate(CODERS):
    unique_coder_id = string.ascii_uppercase[i]
    import_fname = os.path.join(doccano_dir, f"{c}.jsonl")
    with open(import_fname, "r", encoding="utf-8") as infile:
        coder_data = [ json.loads(l) for l in infile.read().splitlines() ]
    # convert from list to a dict that has post id as keys and labels
    coder_data = { post["id"] : post["label"] for post in coder_data }
    data[unique_coder_id] = coder_data

# convert doccano data to a csv with one SECTION/label per row
# and coder/post_id/subtheme as columns
# (so each post has multiple rows)
row_list = []
for coder, coder_data in data.items():
    for post_id, coded_section in coder_data.items():
        for start, end, subtheme in coded_section:
            if subtheme in all_themes:
                df_row = dict(coder=coder, post_id=post_id, subtheme=subtheme)
                row_list.append(df_row)

df = pd.DataFrame(row_list)

# drop duplicates bc sometimes the same theme is there >1 in a single post
df.drop_duplicates(inplace=True, ignore_index=True)

postXtheme = df.groupby("post_id")["subtheme"
    ].value_counts(dropna=False).unstack(fill_value=0
    ).reindex(columns=all_themes, fill_value=0)

postXthemeXcoder = df.groupby(["subtheme","coder"]
    )["post_id"].value_counts(dropna=False
    ).unstack(fill_value=0
    ).reindex(
        pd.MultiIndex.from_product([all_themes, data.keys()], names=["subtheme", "coder"]),
        axis="index", fill_value=0
    )#.T

postXtheme.to_csv(export_fname1, index=True)
postXthemeXcoder.to_csv(export_fname2, index=True)