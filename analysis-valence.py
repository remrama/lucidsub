"""
stats and plot comparing frequency of only-neg and only-post posts

plot has stats written on it
"""
import os
import pandas as pd
import pingouin as pg
import config as c

from statsmodels.stats.proportion import proportions_ztest

import matplotlib.pyplot as plt
plt.rcParams["savefig.dpi"] = 600
plt.rcParams["interactive"] = True
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Arial"
plt.rcParams["mathtext.fontset"] = "custom"
plt.rcParams["mathtext.rm"] = "Arial"
plt.rcParams["mathtext.it"] = "Arial:italic"


import_fname = os.path.join(c.RESULTS_DIR, "themes-highlights_table.csv")
export_fname = os.path.join(c.RESULTS_DIR, "plots", "valence.png")

# all this junk gets down to only the posts with just neg
# or just pos themes (doesn't care how many themes within pos or neg)
ser = pd.read_csv(import_fname, usecols=[0,1],
        index_col="post_id", squeeze=True
    ).replace(c.POS_THEMES, True
    ).replace(c.NEG_THEMES, False
    ).rename("positive"
    ).reset_index(
        ).drop_duplicates(subset=None, # drop duplicated pos or neg within post
        ).drop_duplicates(subset="post_id", keep=False # drop all posts with pos and neg
        ).set_index("post_id"
        ).squeeze()


n_pos = ser.value_counts().loc[True]
n_neg = ser.value_counts().loc[False]
n_obs = ser.size
assert n_obs == n_pos+n_neg

zstat, pval = proportions_ztest(count=n_pos, nobs=n_obs,
    value=.5, alternative="two-sided")


BAR_ARGS = {
    "width" : .8,
    "linewidth" : .5,
    "edgecolor" : "black",
}

xvals = [0, 1]
yvals = [n_pos, n_neg]
colors = [c.POS_COLOR, c.NEG_COLOR]
labels = ["positive\nonly", "negative\nonly"]


_, ax = plt.subplots(figsize=(2, 3), constrained_layout=True)

ax.bar(xvals, yvals, color=colors, **BAR_ARGS)

ax.set_xlim(xvals[0]-.7, xvals[1]+.7)
ax.set_xticks(xvals)
ax.set_xticklabels(labels)

ax.set_ylabel("Number of posts")
ax.set_ybound(upper=100)
ax.yaxis.set(major_locator=plt.MultipleLocator(20),
    minor_locator=plt.MultipleLocator(5))

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

pstr = f"{pval:.3f}".lstrip("0")
stats_txt = f"Z={zstat:.2f}\np={pstr}"
stats_txt = rf"$Z={zstat:.2f}$" + "\n" + rf"$p={pstr}$"
ax.text(1, 1, stats_txt, transform=ax.transAxes,
    fontsize=10, va="top", ha="right")


plt.savefig(export_fname)
plt.close()
