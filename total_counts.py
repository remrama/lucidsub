"""
export a final count table and bargraph
merge the 2 versions and incorporate
resolved disagreements
"""
import os
import pandas as pd

import config as c

import matplotlib.pyplot as plt
plt.rcParams["savefig.dpi"] = 600
plt.rcParams["interactive"] = True
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Arial"


export_fname_table = os.path.join(c.RESULTS_DIR, "themes-total_counts.csv")
export_fname_plot = os.path.join(c.RESULTS_DIR, "plots", "themes-total_counts.png")


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

counts = df.sum().rename("count")

BAR_ARGS = {
    "height" : .8,
    "linewidth" : 1,
    "edgecolor" : "black",
}

themes = (sorted(c.POS_THEMES), sorted(c.NEG_THEMES))
colors = (c.POS_COLOR, c.NEG_COLOR)


# generate axes for pos and neg themes (and extras for showing the max)
_, axes = plt.subplots(ncols=4, figsize=(6,2.5),
    constrained_layout=True,
    gridspec_kw={"width_ratios":[1, .05, 1, .05]})

# separate into axes for drawing and those for showing the max amount
axes4drawing = (axes[0], axes[2])
axes4nothing = (axes[1], axes[3])

# stuff for drawing little slashy lines
EXTENT = 2.5 # proportion of vertical to horizontal extent of the slanted line
slash_args = {
    "marker" : [(-1, -EXTENT), (1, EXTENT)],
    "markersize" : 7,
    "linestyle" : "none",
    "color" : "k",
    "mec" : "k",
    "mew" : 1,
    "clip_on" : False,
}

# draw slashy lines on the "extra" axes
for ax in axes4nothing:
    ax.spines["left"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(left=False, labelleft=False)
    ax.plot([0], [0], transform=ax.transAxes, **slash_args)
    ax.set_xbound(lower=396, upper=400)
    ax.set_xticks([400])

# draw data
for ax, th, col in zip(axes4drawing, themes, colors):
    ax.barh(th, counts.loc[th], color=col, **BAR_ARGS)
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set(major_locator=plt.MultipleLocator(20),
        minor_locator=plt.MultipleLocator(5))
    ax.plot([1], [0], transform=ax.transAxes, **slash_args)
    ax.set_xbound(upper=84)

axes[0].set_xlabel("Number of posts")


# export
plt.savefig(export_fname_plot)
plt.close()

counts.to_csv(export_fname_table)
