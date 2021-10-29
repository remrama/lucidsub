"""
generate a csv with some descriptive stats for each theme

code again stolen from other scripts (so lazy smh)
"""
import os
import json
import glob
import pandas as pd

import config as c


export_fname1 = os.path.join(c.RESULTS_DIR, "themes-descriptivesXtheme.csv")
export_fname2 = os.path.join(c.RESULTS_DIR, "themes-descriptivesXvalence.csv")
export_fname3 = os.path.join(c.RESULTS_DIR, "themes-descriptives_misc.json")


def load_resolved_dataframe(version_number):
    basename1 = f"doccano-postXtheme_v{version_number}.csv"
    basename2 = f"doccano-disagreements2solve_v{version_number}-DONE.xlsx"
    import_fname1 = os.path.join(c.RESULTS_DIR, basename1)
    import_fname2 = os.path.join(c.RESULTS_DIR, basename2)
    df1 = pd.read_csv(import_fname1, index_col="post_id")
    df2 = pd.read_excel(import_fname2, index_col="post_id")
    # binarize the original ratings so any post with all 3 is good
    df1 = df1.eq(3)
    # handle disagreement file
    df2 = df2.loc[df2["keep"], ["theme", "keep"]].pivot(columns="theme"
        ).droplevel(0, 1).reindex_like(df1).fillna(False)
    # merge them
    df = df1 | df2
    return df


df = pd.concat([ load_resolved_dataframe(v) for v in (1, 2) ])

df = df.reset_index(drop=False
    ).melt(id_vars="post_id", var_name="theme", value_name="keep")
df = df[df["keep"]].set_index("post_id").drop(columns="keep")


# load in original raw r/LucidDreaming scrape
import_fname = os.path.join(c.DATA_DIR, "r-LucidDreaming_20210607T232348.csv")
COLUMNS_OF_INTEREST = ["id", "author", "num_comments", "score"]
raw = pd.read_csv(import_fname,
        index_col="id", usecols=COLUMNS_OF_INTEREST, low_memory=False
    ).rename_axis("post_id")

df = df.join(raw, how="left")

df["theme_valence"] = df["theme"].apply(
    lambda x: "positive" if x in c.POS_THEMES else "negative")


dfXtheme = df.reset_index().groupby("theme"
    ).agg({
        "post_id" : "nunique",
        "author": "nunique",
        "num_comments": "median",
        "score": "median",
    }).rename(columns={
        "post_id" : "nunique_posts",
        "author" : "nunique_authors",
        "num_comments" : "n_comments-median",
        "score" : "score-median",
    }).reindex(c.POS_THEMES+c.NEG_THEMES)

dfXtheme.insert(0, "pct_of_total",
    (dfXtheme.nunique_posts / 400).multiply(100).round(1)
)


dfXvalence = df.reset_index(
    ).drop_duplicates(subset=["theme_valence", "post_id"]
    ).groupby("theme_valence"
    ).agg({
        "post_id" : "nunique",
        "author": "nunique",
        "num_comments": "median",
        "score": "median",
    }).rename(columns={
        "post_id" : "nunique_posts",
        "author" : "nunique_authors",
        "num_comments" : "n_comments-median",
        "score" : "score-median",
    })

dfXvalence.insert(0, "pct_of_total",
    (dfXvalence.nunique_posts / 400).multiply(100).round(1)
)

total_info = {
    "nunique_posts" : df.index.nunique(),
    "nunique_users" : df["author"].nunique(),
    "n_theme_labels" :  int(dfXtheme.nunique_posts.sum()),
    "n_max_posts_per_user" : df.author.value_counts().max(),
    "n_themes_per_post" : df.groupby("post_id").theme.nunique().value_counts().to_dict(),
}



dfXtheme.to_csv(export_fname1, index=True)
dfXvalence.to_csv(export_fname2, index=True)
with open(export_fname3, "w", encoding="utf-8") as f:
    json.dump(total_info, f, indent=True)
