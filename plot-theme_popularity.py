"""Visualize theme popularity.
"""
import os
import pandas as pd
import utils

import matplotlib.pyplot as plt
utils.load_matplotlib_settings()


import_basename = "themes-descriptives.csv"
export_basename = "themes-popularity.png"
import_fullpath = os.path.join(utils.Config.data_directory, "results", import_basename)
export_fullpath = import_fullpath.replace(import_basename, export_basename)


# Load data.
descr = pd.read_csv(import_fullpath)

# Extract data for plotting.
descr = descr[:-2] # remove pos/neg summary scores
themes = descr["theme"].tolist()
upvotes = descr["score-median"].tolist()
comments = descr["n-comments-median"].tolist()

FIGSIZE = (5, 3)
BAR_ARGS = {
    "width" : .4,
    "linewidth" : .5,
    "edgecolor" : "black",
}
ALPHAS = {
    "upvotes": 1,
    "comments": .3,
}

# Open figure and add second/twin axis.
fig, ax1 = plt.subplots(figsize=FIGSIZE, constrained_layout=True)
ax2 = ax1.twinx()

# Get positive and negative theme names for coloring.
pos_themes = sorted(utils.Config.themes.positive)
neg_themes = sorted(utils.Config.themes.negative)

# Draw.
n_themes = len(themes)
upvote_xvals = [ i-BAR_ARGS["width"]/2 for i in range(n_themes) ]
comment_xvals = [ i+BAR_ARGS["width"]/2 for i in range(n_themes) ]
upvote_bars = ax1.bar(upvote_xvals, upvotes, alpha=ALPHAS["upvotes"], **BAR_ARGS)
comment_bars = ax2.bar(comment_xvals, comments, alpha=ALPHAS["comments"], **BAR_ARGS)
for th, b1, b2 in zip(themes, upvote_bars, comment_bars):
    color = utils.Config.colors.positive if th in pos_themes else utils.Config.colors.negative
    b1.set_facecolor(color)
    b2.set_facecolor(color)

# Aesthetics.
# ax.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)
ax2.spines[["top", "bottom", "left"]].set_visible(False)
ax1.set_ylim(0, 10)
ax2.set_ylim(0, 10)
ax1.set_xticks(range(n_themes))
ax1.set_xticklabels(themes, rotation=33, ha="right")
ax1.set_ylabel("Median upvote score")
ax2.set_ylabel("Median number of comments", rotation=270, va="bottom")
# ax.set_title(title, weight="bold", pad=1)
ax2.yaxis.label.set_alpha(ALPHAS["comments"])
ax2.spines["right"].set_alpha(ALPHAS["comments"])
ax2.tick_params(axis="y",
    color=[0, 0, 0, ALPHAS["comments"]],
    labelcolor=[0, 0, 0, ALPHAS["comments"]])


# Export
plt.savefig(export_fullpath)
utils.save_hires_copies(export_fullpath)
plt.close()
