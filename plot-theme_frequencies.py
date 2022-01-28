"""Visualize final themes frequencies.
"""
import os
import pandas as pd
import utils

import matplotlib.pyplot as plt
utils.load_matplotlib_settings()


basename = "themes-frequencies.csv"
import_fullpath = os.path.join(utils.Config.data_directory, "results", basename)
export_fullpath = import_fullpath.replace(".csv", ".png")


# Load data.
freq_series = pd.read_csv(import_fullpath, index_col="theme", squeeze=True)


FIGSIZE = (5, 2)
YMAX = 80
YTICK_MAJOR = 20
YTICK_MINOR = 5
BAR_ARGS = {
    "height" : .8,
    "linewidth" : 1,
    "edgecolor" : "black",
}

# Open figure with 2 subplots, 1 for pos 1 for neg.
fig, axes = plt.subplots(ncols=2, figsize=FIGSIZE,
    gridspec_kw=dict(wspace=1.5, left=.25, right=.95, bottom=.2, top=.9))

# Set tuples to iterate over, for the 2 valence subplots of panel A.
themes = (sorted(utils.Config.themes.positive), sorted(utils.Config.themes.negative))
colors = (utils.Config.colors.positive, utils.Config.colors.negative)
titles = ("Positive themes", "Negative themes")

# Draw subplots.
for ax, theme, color, title in zip(axes, themes, colors, titles):
    ax.barh(theme, freq_series.loc[theme], color=color, **BAR_ARGS)
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set(major_locator=plt.MultipleLocator(YTICK_MAJOR),
                 minor_locator=plt.MultipleLocator(YTICK_MINOR))
    ax.set_title(title, weight="bold")
    ax.set_xbound(upper=YMAX)
    # if ax.get_subplotspec().is_first_col():
    ax.set_xlabel("Post frequency")


# Export
plt.savefig(export_fullpath)
utils.save_hires_copies(export_fullpath)
plt.close()
