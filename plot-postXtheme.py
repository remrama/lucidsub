"""Visualize the (dis)agreement between coders.
Specifically, the number of coders per post that selected each theme.
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

import_basename = f"doccano-postXtheme_2019{month_cap}.csv"
export_basename = f"doccano-postXtheme_2019{month_cap}.png"
import_fullpath = os.path.join(utils.Config.data_directory, "derivatives", import_basename)
export_fullpath = os.path.join(utils.Config.data_directory, "results", export_basename)


# Load and manipulate data.
df = pd.read_csv(import_fullpath, index_col="post_id")
data = df.T.values

masked_data = np.ma.masked_where(data == 0, data)
n_coders = len(utils.Config.coders)
n_pos_themes = len(utils.Config.themes.positive)
n_neg_themes = len(utils.Config.themes.negative)
pos_data = masked_data[:n_pos_themes, :]
neg_data = masked_data[n_pos_themes:, :]
height_ratios = [n_pos_themes, n_neg_themes]

IMSHOW_ARGS = {
    "vmin": 0,
    "vmax": n_coders,
    "origin": "upper",
    "aspect": "auto",
    "interpolation": "none",
}

CBAR_LABEL_ARGS = {
    "labelpad": 6,
    "rotation": 270,
    "fontsize": 8,
    "verticalalignment": "center",
    "horizontalalignment": "center",
}

# Open figure.
fig, axes = plt.subplots(2, 2, figsize=(6,2.5),
    gridspec_kw=dict(height_ratios=height_ratios, width_ratios=[1,.02]),
    constrained_layout=True)

ax1, cbar_ax1, ax2, cbar_ax2 = axes.flat

# Draw.
im1 = ax1.imshow(pos_data, cmap="Greens", **IMSHOW_ARGS)
im2 = ax2.imshow(neg_data, cmap="Reds", **IMSHOW_ARGS)

# Looks.
ax1.set_yticks(range(n_pos_themes))
ax2.set_yticks(range(n_neg_themes))
ax1.set_yticklabels(utils.Config.themes.positive, fontsize=8)
ax2.set_yticklabels(utils.Config.themes.negative, fontsize=8)
ax1.xaxis.set(major_locator=plt.NullLocator())
ax2.xaxis.set(major_locator=plt.NullLocator())
ax2.set_xlabel(r"$\leftarrow$unique posts$\rightarrow$", fontsize=8)

# Add colorbars.
cbar1 = fig.colorbar(im1, cax=cbar_ax1, orientation="vertical")
cbar2 = fig.colorbar(im2, cax=cbar_ax2, orientation="vertical")
cbar1.ax.tick_params(which="major", color="black", size=3, direction="in", labelsize=8)
cbar2.ax.tick_params(which="major", color="black", size=3, direction="in", labelsize=8)
cbar1.ax.tick_params(which="minor", color="black", size=2, direction="in")
cbar2.ax.tick_params(which="minor", color="black", size=2, direction="in")
cbar1.ax.yaxis.set(major_locator=plt.MultipleLocator(n_coders), minor_locator=plt.MultipleLocator(1))
cbar2.ax.yaxis.set(major_locator=plt.MultipleLocator(n_coders), minor_locator=plt.MultipleLocator(1))
cbar1.set_label("# of coders", **CBAR_LABEL_ARGS)
cbar2.set_label("# of coders", **CBAR_LABEL_ARGS)

# Export.
plt.savefig(export_fullpath)
utils.save_hires_copies(export_fullpath)
plt.close()