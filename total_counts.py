"""
export a final count table and bargraph

also plot the valence frequency comparison
"""
import os
import json
import pandas as pd

import config as c

import matplotlib.pyplot as plt
plt.rcParams["savefig.dpi"] = 600
plt.rcParams["interactive"] = True
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Arial"


export_fname_table = os.path.join(c.RESULTS_DIR, "themes-total_counts.csv")
export_fname_plot = os.path.join(c.RESULTS_DIR, "plots", "themes-total_counts.png")


################## Panel A data

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


counts.to_csv(export_fname_table)



################## Panel B data

import_fname = os.path.join(c.RESULTS_DIR, "valence.json")
with open(import_fname, "rt", encoding="utf-8") as f:
    valence_stats = json.load(f)




########### open plot


bar_args = {
    "height" : .8,
    "linewidth" : 1,
    "edgecolor" : "black",
}



FIGSIZE = (7.5, 2.5)

fig = plt.figure(figsize=FIGSIZE, constrained_layout=False) 
gs1 = fig.add_gridspec(ncols=2, wspace=1.7,
    left=.2, right=.7, bottom=.2, top=.9) 
axes = gs1.subplots()
gs2 = fig.add_gridspec(left=.83, right=1, bottom=.2, top=.9) 
ax3 = gs2.subplots()


fig.text(0, 1, "A", fontsize=12, fontweight="bold", ha="left", va="top")
fig.text(.75, 1, "B", fontsize=12, fontweight="bold", ha="left", va="top")


# draw Panel A

themes = (sorted(c.POS_THEMES), sorted(c.NEG_THEMES))
colors = (c.POS_COLOR, c.NEG_COLOR)
titles = ("Positive themes", "Negative themes")

for ax, th, col, titl in zip(axes, themes, colors, titles):
    ax.barh(th, counts.loc[th], color=col, **bar_args)
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set(major_locator=plt.MultipleLocator(20),
        minor_locator=plt.MultipleLocator(5))
    ax.set_title(titl, fontsize=10, weight="bold")

    ax.set_xbound(upper=80)
    if ax.get_subplotspec().is_first_col():
        ax.set_xlabel("Number of posts")


# draw Panel B

xvals = [0, 1]
yvals = [ valence_stats["n_positive"], valence_stats["n_negative"] ]
colors = [c.POS_COLOR, c.NEG_COLOR]
labels = ["positive\nonly", "negative\nonly"]


bar_args["width"] = bar_args.pop("height")

ax3.bar(xvals, yvals, color=colors, **bar_args)

ax3.set_xlim(xvals[0]-.7, xvals[1]+.7)
ax3.set_xticks(xvals)
ax3.set_xticklabels(labels)

ax3.hlines(90, xmin=0, xmax=1, color="k", lw=2, capstyle="round")
ax3.text(.5, 90, "n.s.", fontsize=8, va="bottom", ha="center")

ax3.set_ylabel("Number of posts", labelpad=0)
ax3.set_ybound(upper=100)
ax3.yaxis.set(major_locator=plt.MultipleLocator(20),
    minor_locator=plt.MultipleLocator(5))

ax3.spines["top"].set_visible(False)
ax3.spines["right"].set_visible(False)



############## export
plt.savefig(export_fname_plot)
plt.close()

