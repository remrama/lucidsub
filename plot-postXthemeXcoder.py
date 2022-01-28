"""Visualize the (dis)agreement between coders.
Specifically, the number of coders per post that selected each theme
and also consistency between coders.
"""
import os
import argparse
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

import utils

utils.load_matplotlib_settings()


parser = argparse.ArgumentParser()
parser.add_argument("-m", "--month", type=str, required=True, help="Month is needed to load/export proper filenames now")
args = parser.parse_args()

MONTH_STR = args.month
month_cap = MONTH_STR.capitalize()

import_basename = f"doccano-postXthemeXcoder_2019{month_cap}.csv"
export_basename = f"doccano-postXthemeXcoder_2019{month_cap}.png"
import_fullpath = os.path.join(utils.Config.data_directory, "derivatives", import_basename)
export_fullpath = os.path.join(utils.Config.data_directory, "results", export_basename)


# Load data.
df = pd.read_csv(import_fullpath, index_col=["subtheme", "coder"])
df = df.T

all_themes = utils.Config.themes.positive + utils.Config.themes.negative
n_themes = len(all_themes)
n_coders = len(utils.Config.coders)

# Open figure.
fig, axes = plt.subplots(1, n_themes, figsize=(.4*n_themes, 3),
    constrained_layout=True)

# Draw.
for ax, theme in zip(axes, all_themes):
    plot_df = df[theme]
    plot_data = plot_df.values
    masked_data = np.ma.masked_where(plot_data == 0, plot_data)
    cmap = "Greens" if theme in utils.Config.themes.positive else "Reds"
    im = ax.imshow(masked_data, cmap=cmap,
        vmin=0, vmax=1, origin="upper", aspect="auto", interpolation="none")
    ax.set_yticks([])
    ax.set_title(theme.replace(" ", "\n"),
        fontsize=8, rotation=90, ha="center", va="bottom")
    if ax.get_subplotspec().is_first_col():
        ax.set_xticks(range(n_coders))
        ax.set_xticklabels(plot_df.columns.tolist(), fontsize=8)
        ax.set_xlabel("coder", fontsize=8)
        ax.set_ylabel(r"$\leftarrow$unique posts$\rightarrow$", fontsize=8)
    else:
        ax.set_xticks([])
    ax.hlines(
        np.linspace(*ax.get_ylim()[::-1], len(plot_df)+1),
        ax.get_xbound()[0], ax.get_xbound()[1],
        linewidth=.2, alpha=.5, color="gainsboro")


# Export.
plt.savefig(export_fullpath)
utils.save_hires_copies(export_fullpath, skip_extensions=["eps"])
plt.close()