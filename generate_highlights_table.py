"""Export a table with all highlighted (ie, "themed") content.

It's not for analysis, but just to look through for examples.

This code is a bit chaotic and not well-commented,
but it's not for any formal analyses so...
"""
import os
import json
import glob
import string
import pandas as pd
import utils

export_basename = "themes-highlights.csv"
export_fullpath = os.path.join(utils.Config.data_directory, "derivatives", export_basename)



# get a list of the post_id/theme combos in the final set
final_df = utils.load_final_post_themes(utils.Config)
final_df = final_df.reset_index(drop=False
    ).melt(id_vars="post_id", var_name="theme", value_name="keep")
final_df = final_df[final_df["keep"]].reset_index(drop=True).drop(columns="keep")
keepers = final_df.groupby("theme").post_id.apply(list).to_dict()

# load in all the raw doccano output (for the highlights)
# get a list of the 2 filenames from 2 different versions
glob_str = os.path.join(utils.Config.data_directory, "source", "doccano-2019*")
doccano_dirs = glob.glob(glob_str)
assert len(doccano_dirs) == 2

rows = []
for d in doccano_dirs:
    for coder in utils.Config.coders:
        import_fn = os.path.join(d, f"{coder}.jsonl")
        with open(import_fn, "r", encoding="utf-8") as f:
            coder_data = [ json.loads(l) for l in f.read().splitlines() ]
        for post in coder_data:
            post_id = post["id"]
            full_txt = post["data"]
            theme_list = post["label"]
            for start_indx, end_indx, theme in theme_list:
                theme = "Lucid dysphoria" if theme == "Lucid nightmares" else theme
                theme = "Positive waking mood" if theme == "Positive morning mood" else theme
                highlight_txt = full_txt[start_indx:end_indx]
                row_data = {
                    "coder" : coder,
                    "post_id" : post_id,
                    "full_txt" : full_txt,
                    "highlight_txt" : highlight_txt,
                    "theme" : theme,
                }
                rows.append(row_data)


df = pd.DataFrame(rows)

coder_renaming = { c: "coder_"+string.ascii_uppercase[i]+"_txt"
    for i, c in enumerate(utils.Config.coders) }


# get rid of unused themes from part 1
theme_order = sorted(utils.Config.themes.positive) + sorted(utils.Config.themes.negative)
df = df[df["theme"].isin(theme_order)].reset_index(drop=True)


# only keep those that passed disagreement resolution
keeper_func = lambda row: row["post_id"] in keepers[row["theme"]]
df = df[df.apply(keeper_func, axis=1)].reset_index(drop=True)

# merge all highlights of a given post for a given user
# then pivot to get all highlights in the same row
df = df.groupby(["post_id", "coder", "theme", "full_txt"]
    ).highlight_txt.apply(lambda ser: ser.str.cat(sep="[:::]")
    ).reset_index(drop=False
    ).pivot(columns="coder", values="highlight_txt",
            index=["theme", "post_id", "full_txt"]
    ).reset_index(["post_id", "full_txt"]
    ).rename(columns=coder_renaming
    ).sort_index(key=lambda index: index.map(lambda t: theme_order.index(t)))

df.columns = df.columns.values # to get rid of meaningless column index name

coder_columns = sorted(coder_renaming.values())

# sort within theme in some meaningful way
# so that the top of the theme section has those
# with most consistency (eg, all 3 highlighted something)
### this is all so incredibly hacky, but w/e it's not necessary anyways
df["n_coders_highlight"] = df[coder_columns].notnull().sum(axis=1)
def readability_order(row):
    coder_true = row[coder_columns].notnull()
    n_coders = coder_true.sum()
    if n_coders == 2:
        # prefer when it's the first 2
        # then 1st and 3rd, then 2nd and 3rd
        if coder_true[0] and coder_true[1]:
            n_coders = 2.2
        elif coder_true[0] and coder_true[2]:
            n_coders = 2.1
    if n_coders == 1:
        n_coders -= .1*[ i for i, x in enumerate(coder_true) if x ][0]
    return n_coders

# this is hackey but I don't see another way rn
df["theme_order"] = df.index.map(lambda t: theme_order.index(t))
df["readability_order"] = df.apply(readability_order, axis=1)
df = df.sort_values(
        ["theme_order", "readability_order", "post_id"],
        ascending=[True, False, True]
    ).drop(columns=["theme_order", "readability_order"])

# reorder columns so it's A, B, C
# column_order = ["post_id", "full_txt", "n_coders_highlight"] + coder_columns
column_order = ["post_id", "full_txt"] + coder_columns + ["n_coders_highlight"]
df = df[column_order]

df.to_csv(export_fullpath, index=True, na_rep="NA")
