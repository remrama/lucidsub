"""
"""
import os
import json
import string
import pandas as pd

######### variable

IMPORT_DIR = "../data/20210822"
RESULTS_DIR = "../results"

POS_COLOR = "#4CAF50"
NEG_COLOR = "#F44336" 


CODERS = ["remym", "lsowin", "rraider", "hcaldas", "hadaweh"] #"cmader", "kkonkoly"]

n_coders = len(CODERS)

coder_mappings = { c: string.ascii_uppercase[i] for i, c in enumerate(CODERS) }

with open("../code/labels.json", "r") as infile:
    themes = [ label["text"] for label in json.load(infile) ]

n_themes = len(themes)

n_pos_themes = themes.index("Sleep paralysis")
n_neg_themes = len(themes) - n_pos_themes


def load_data():

    data = {}
    for i, c in enumerate(CODERS):
        coder_id = coder_mappings[c]
        import_fname = os.path.join(IMPORT_DIR, f"{c}.jsonl")
        with open(import_fname, "r") as infile:
            coder_data = [ json.loads(l) for l in infile.read().splitlines() ]
        # convert from list to a dict that has post id as keys and labels
        coder_data = { post["id"] : post["label"] for post in coder_data }
        data[coder_id] = coder_data

    row_list = []
    for coder, coderdata in data.items():
        for postid, postlabels in coderdata.items():
            for start, end, theme in postlabels:
                payload = dict(coder=coder, postid=postid, theme=theme)
                row_list.append(payload)
    df = pd.DataFrame(row_list)

    # drop duplicates bc sometimes the same theme is there >1 in a single post
    df = df.drop_duplicates().reset_index(drop=True)

    return df
    

def aggregate_codersXtheme(df):
    """expects a dataframe with 3 columns
    theme, coder, postid
    """
    # make sure the dataframe includes ALL themes and posts
    # even if they're not in the raw dataframe bc never used

    ## load datafile to make sure all 200 posts are there, even
    ## though not all 200 were coded as anything
    all_post_ids = pd.read_csv("../data/r-LucidDreaming_2020April+200.csv"
        )["id"].tolist()

    full_indx = pd.MultiIndex.from_product(
        [themes, list(coder_mappings.values())],
        names=["theme", "coder"])
    
    big_df = df.groupby(["theme","coder"]
        )["postid"].value_counts(dropna=False
        ).unstack(fill_value=0
        ).reindex(index=full_indx, columns=all_post_ids, fill_value=0
        )#.T

    # expanded = big_df.groupby("theme").sum().mean(axis=1).reindex(themes)
    # # expanded = df.groupby("theme")["postid"
    # #     ].value_counts(dropna=False
    # #     ).unstack(fill_value=0
    # #     ).reindex(index=themes, columns=all_post_ids, fill_value=0)
    return big_df



