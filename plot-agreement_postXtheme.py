"""visualize the (dis)agreement between coders
"""
import os
import argparse
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

import config as c

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--version", type=int, required=True, choices=[1, 2])
args = parser.parse_args()

version = args.version

plt.rcParams["savefig.dpi"] = 600
plt.rcParams["interactive"] = True
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Arial"
plt.rcParams["mathtext.fontset"] = "custom"
plt.rcParams["mathtext.rm"] = "Arial"
plt.rcParams["mathtext.it"] = "Arial:italic"
plt.rcParams["mathtext.bf"] = "Arial:bold"


import_fname = os.path.join(c.RESULTS_DIR, f"doccano-postXtheme_v{version}.csv")
export_fname = os.path.join(c.RESULTS_DIR, "plots", f"doccano-postXtheme_v{version}.png")

df = pd.read_csv(import_fname, index_col="post_id")

data = df.T.values

masked_data = np.ma.masked_where(data == 0, data)

n_coders = len(c.CODERS)
n_pos_themes = len(c.POS_THEMES)
n_neg_themes = len(c.NEG_THEMES)
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


fig, axes = plt.subplots(2, 2, figsize=(6,2.5),
    gridspec_kw=dict(height_ratios=height_ratios, width_ratios=[1,.02]),
    constrained_layout=True)

ax1, cbar_ax1, ax2, cbar_ax2 = axes.flat

im1 = ax1.imshow(pos_data, cmap=c.POS_COLORMAP, **IMSHOW_ARGS)
im2 = ax2.imshow(neg_data, cmap=c.NEG_COLORMAP, **IMSHOW_ARGS)

ax1.set_yticks(range(n_pos_themes))
ax2.set_yticks(range(n_neg_themes))
ax1.set_yticklabels(c.POS_THEMES, fontsize=8)
ax2.set_yticklabels(c.NEG_THEMES, fontsize=8)

ax1.xaxis.set(major_locator=plt.NullLocator())
ax2.xaxis.set(major_locator=plt.NullLocator())

ax2.set_xlabel(r"$\leftarrow$unique posts$\rightarrow$", fontsize=8)

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


plt.savefig(export_fname)
plt.close()