"""
export a final count table and bargraph
merge the 2 versions and incorporate
resolved disagreements
"""
import os
import pandas as pd

import config as c

# import seaborn as sea
import matplotlib.pyplot as plt
plt.rcParams["savefig.dpi"] = 600
plt.rcParams["interactive"] = True
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Arial"


export_fname_table = os.path.join(c.RESULTS_DIR, "total_counts.csv")
export_fname_plot = os.path.join(c.RESULTS_DIR, "plots", "total_counts.png")


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


# df_v1 = load_resolved_dataframe(1)
# df_v2 = load_resolved_dataframe(2)
df = pd.concat([ load_resolved_dataframe(v) for v in (1, 2) ])

counts = df.sum().rename("count")

BAR_ARGS = {
    "height" : .8,
    "linewidth" : 1,
    "edgecolor" : "black",
}

# themes = (c.POS_THEMES, c.NEG_THEMES)
themes = (sorted(c.POS_THEMES), sorted(c.NEG_THEMES))
colors = (c.POS_COLOR, c.NEG_COLOR)

_, axes = plt.subplots(ncols=2, figsize=(6,2.5),
    sharex=True, constrained_layout=True)

for ax, th, col in zip(axes, themes, colors):
    ax.barh(th, counts.loc[th], color=col, **BAR_ARGS)
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set(major_locator=plt.MultipleLocator(20),
        minor_locator=plt.MultipleLocator(5))

ax.set_xbound(upper=80)

plt.savefig(export_fname_plot)
plt.close()

counts.to_csv(export_fname_table)