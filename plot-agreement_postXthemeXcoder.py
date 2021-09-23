"""visualize the (dis)agreement between coders
*more detailed
"""
import os
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

import config as c


plt.rcParams["savefig.dpi"] = 600
plt.rcParams["interactive"] = True
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Arial"
plt.rcParams["mathtext.fontset"] = "custom"
plt.rcParams["mathtext.rm"] = "Arial"
plt.rcParams["mathtext.it"] = "Arial:italic"
plt.rcParams["mathtext.bf"] = "Arial:bold"


import_fname = os.path.join(c.RESULTS_DIR, "doccano-postXthemeXcoder.csv")
export_fname = os.path.join(c.RESULTS_DIR, "plots", "doccano-postXthemeXcoder.png")

df = pd.read_csv(import_fname, index_col=["subtheme", "coder"])

df = df.T

all_themes = c.POS_THEMES + c.NEG_THEMES
n_themes = len(all_themes)
n_coders = len(c.CODERS)

fig, axes = plt.subplots(1, n_themes, figsize=(.4*n_themes, 3),
    constrained_layout=True)

for ax, theme in zip(axes, all_themes):
    plot_df = df[theme]
    plot_data = plot_df.values
    masked_data = np.ma.masked_where(plot_data == 0, plot_data)
    cmap = c.POS_COLORMAP if theme in c.POS_THEMES else c.NEG_COLORMAP
    im = ax.imshow(masked_data, cmap=cmap,
        vmin=0, vmax=1, origin="upper", aspect="auto", interpolation="none")
    ax.set_yticks([])
    ax.set_title(theme.replace(" ", "\n"),
        fontsize=8, rotation=90, ha="center", va="bottom")
    if ax.get_subplotspec().is_first_col():
        # ax.xaxis.tick_top()
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


plt.savefig(export_fname)
plt.close()