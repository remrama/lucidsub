"""Generate some descriptive stats for each theme
and for the total dataset (each their own csv).

Things like number of unique users, percentage of total,
and some populary-related values (e.g., number of comments attached)
"""
import os
import pandas as pd
import utils

export_basename1 = "themes-descriptives.csv"
export_basename2 = "corpus-descriptives.csv"
export_fullpath1 = os.path.join(utils.Config.data_directory, "results", export_basename1)
export_fullpath2 = os.path.join(utils.Config.data_directory, "results", export_basename2)


# Load the full/final dataset of themes for each post.
df = utils.load_final_post_themes(utils.Config)

df = df.reset_index(drop=False
    ).melt(id_vars="post_id", var_name="theme", value_name="keep")
df = df[df["keep"]].set_index("post_id").drop(columns="keep")


# Load the full original r/LucidDreaming scrape, for comments/upvote scores.
COLUMNS_OF_INTEREST = ["id", "author", "num_comments", "score"]
basename = f"r-LucidDreaming_{utils.Config.scrape_timestamp}.csv"
import_fname = os.path.join(utils.Config.data_directory, "source", basename)
raw = pd.read_csv(import_fname, index_col="id",
                  usecols=COLUMNS_OF_INTEREST,
                  encoding="utf-8-sig", low_memory=False
    ).rename_axis("post_id")


# Merge the two, keeping only analyzed posts
# so the post attributes are attached to the relevant posts.
df = df.join(raw, how="left")

# Create column of just valence.
def name2valence(theme):
    if theme in utils.Config.themes.positive:
        return "positive"
    elif theme in utils.Config.themes.negative:
        return "negative"
    else:
        raise ValueError(f"Unexpected theme name: {theme}")

df["theme_valence"] = df["theme"].map(name2valence)


AGGREGATIONS = {
    "post_id"      : "nunique",
    "author"       : "nunique",
    "num_comments" : "median",
    "score"        : "median",
}

RENAMINGS = {
    "post_id"      : "n-unique-posts",
    "author"       : "n-unique-authors",
    "num_comments" : "n-comments-median",
    "score"        : "score-median",
}

# Generate a dataframe tallying social scores for each theme.
dfXtheme = df.reset_index().groupby("theme"
    ).agg(AGGREGATIONS).rename(columns=RENAMINGS
    ).reindex(utils.Config.themes.positive + utils.Config.themes.negative)

# Add percentage column.
dfXtheme.insert(0, "pct-unique-posts",
    dfXtheme["n-unique-posts"].div(400).multiply(100).round())

# Same as before, but within each valence.
dfXvalence = df.reset_index(
    ).drop_duplicates(subset=["theme_valence", "post_id"]
    ).groupby("theme_valence"
    ).agg(AGGREGATIONS).rename(columns=RENAMINGS
    ).reindex(["positive", "negative"])
dfXvalence.insert(0, "pct-unique-posts",
    dfXvalence["n-unique-posts"].div(400).multiply(100).round())

# Combine and export.
dfX = pd.concat([dfXtheme, dfXvalence], axis=0)
dfX.to_csv(export_fullpath1, index_label="theme")



############ Generate stats of the whole corpus.

n_posts_with_x_themes = df.groupby("post_id"
    )["theme"].nunique().value_counts().to_dict()

n_posts_with_x_themes = { f"n-posts-with-{k}-themes" : v
    for k, v in n_posts_with_x_themes.items() }

stats_for_total_corpus = {
    "n-unique-posts" : df.index.nunique(),
    "n-unique-users" : df["author"].nunique(),
    "n-theme-labels" : dfXtheme["n-unique-posts"].sum(),
    "n-max-posts-per-user" : df["author"].value_counts().max(),
}

# Merge the dictionaries.
stats_for_total_corpus = stats_for_total_corpus | n_posts_with_x_themes 

# Export.
series = pd.Series(stats_for_total_corpus, name="value")
series.to_csv(export_fullpath2, index_label="statistic", encoding="utf-8")
