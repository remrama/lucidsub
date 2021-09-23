
from config import *

import os
import numpy as np
import pandas as pd

import_fname = os.path.join(RESULTS_DIR, "irr_multi.csv")

df = pd.read_csv(import_fname)

themes = df["theme"].tolist()
alphas = df["krippendorff_alpha"].tolist()

def my_formatter(x, pos):
    val_str = '{:g}'.format(x)
    return val_str.replace("0", "", 1) if np.abs(x) > 0 and np.abs(x) < 1 else val_str


fig, axes = plt.subplots(2, figsize=(3,4), constrained_layout=True,
    gridspec_kw={"height_ratios":[n_pos_themes, n_neg_themes]},
    sharex=True, sharey=False)

BAR_ARGS = dict(edgecolor="k", linewidth=1, height=.8)

for ax in axes:
    if ax.is_first_row():
        x = themes[:n_pos_themes]
        y1 = alphas[:n_pos_themes]
        color = POS_COLOR
    else:
        x = themes[n_pos_themes:]
        y1 = alphas[n_pos_themes:]
        color = NEG_COLOR
    ax.barh(x, y1, color=color, **BAR_ARGS)

    ax.axvline(0, color="k", lw=1, linestyle="-")
    # ax.axvline(.8, color="gold", lw=1, linestyle="--")

    ax.set_xbound(lower=-.1, upper=1)
    ax.xaxis.set(major_formatter=plt.FuncFormatter(my_formatter),
        major_locator=plt.MultipleLocator(.5),
        minor_locator=plt.MultipleLocator(.1))
    ax.tick_params(axis="both", which="major", labelsize=8)
    ax.invert_yaxis()

    ax.grid(axis="x", which="major", lw=1, ls="-", alpha=.5)
    ax.grid(axis="x", which="minor", lw=.5, ls="-", alpha=.5)
    ax.set_axisbelow(True)

ax.set_xlabel("Krippendorff's alpha", fontsize=8)

export_fname = os.path.join(RESULTS_DIR, "irr_alpha.png")
plt.savefig(export_fname)
plt.close()

