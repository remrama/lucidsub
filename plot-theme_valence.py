"""Visualize positive-only and negative-only post frequencies.
"""
import os
import pandas as pd
import utils
import matplotlib.pyplot as plt
utils.load_matplotlib_settings()

# I/O
basename = "themes-valence.csv"
import_fullpath = os.path.join(utils.Config.data_directory, "results", basename)
export_fullpath = import_fullpath.replace(".csv", ".png")

# Load data.
stats = pd.read_csv(import_fullpath, index_col="statistic", squeeze=True)

# Select some plotting variables.
FIGSIZE = (1.5, 2)
YMAX = 100
YTICK_MAJOR = 20
YTICK_MINOR = 5
BAR_ARGS = {
    "width" : .8,
    "linewidth" : 1,
    "edgecolor" : "black",
}

# Extract data for plotting
xvals = [0, 1]
yvals = stats.loc[["n-positive-only","n-negative-only"]].values
colors = [utils.Config.colors.positive, utils.Config.colors.negative]
labels = ["Positive\nonly", "Negative\nonly"]

# Open figure.
fig, ax = plt.subplots(figsize=FIGSIZE, constrained_layout=True)

# Draw data.
ax.bar(xvals, yvals, color=colors, **BAR_ARGS)

# Significance marker.
assert stats.loc["p-val"] > .05, "Expected to be no effect here."
ax.hlines(90, xmin=0, xmax=1, color="k", lw=2, capstyle="round")
ax.text(.5, 90, "n.s.", va="bottom", ha="center")

# Visual adjustments.
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_xlim(xvals[0]-.7, xvals[1]+.7)
ax.set_xticks(xvals)
ax.set_xticklabels(labels)
ax.set_ylabel("Post frequency", labelpad=0)
ax.set_ybound(upper=YMAX)
ax.yaxis.set(major_locator=plt.MultipleLocator(YTICK_MAJOR),
             minor_locator=plt.MultipleLocator(YTICK_MINOR))

# Export
plt.savefig(export_fullpath)
utils.save_hires_copies(export_fullpath)
plt.close()
