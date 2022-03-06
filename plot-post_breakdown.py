"""Visualize how many posts were used and became pos/neg/mixed.
"""
import os
import numpy as np
import pandas as pd
import utils

import matplotlib.pyplot as plt
utils.load_matplotlib_settings()


############### I/O and loading data.

export_basename = "post-breakdown.png"
export_fullpath = os.path.join(utils.Config.data_directory, "results", export_basename)

import_basename = "themes-valence.csv"
import_fullpath = os.path.join(utils.Config.data_directory, "results", import_basename)

ser = pd.read_csv(import_fullpath, index_col="statistic", squeeze=True)

N_SAMPLESIZE = 400


### Extract data and plot variables for pie chart.

n_positive_only_posts = ser.loc["n-positive-only"]
n_negative_only_posts = ser.loc["n-negative-only"]
n_mixed_posts = N_SAMPLESIZE - n_positive_only_posts - n_negative_only_posts

title = f"{N_SAMPLESIZE} posts evaluated"

wedge_data = {
    "total" : dict(size=N_SAMPLESIZE, color="white",
        label="No theme"),
    "mixed" : dict(size=n_mixed_posts, color="gainsboro",
        label="Mixed\nvalence"),
    "pos" : dict(size=n_positive_only_posts, color=utils.Config.colors.positive,
        label="Positive-only\nvalence"),
    "neg" : dict(size=n_positive_only_posts, color=utils.Config.colors.negative,
        label="Negative-only\nvalence"),
}

WEDGE_ORDER = ["total", "mixed", "pos", "neg"]

sizes = [ wedge_data[w]["size"] for w in WEDGE_ORDER ]
colors = [ wedge_data[w]["color"] for w in WEDGE_ORDER ]
labels = [ wedge_data[w]["label"] for w in WEDGE_ORDER ]

PIE_KWARGS = dict(startangle=180, radius=1, shadow=False,
    pctdistance=.7, labeldistance=.35, rotatelabels=False)
PIE_WEDGE_KWARGS = dict(linewidth=.2, edgecolor="black", alpha=1)
PIE_TEXT_KWARGS = dict(color="black", linespacing=.8)
ANNOTATE_KWARGS = dict(
    zorder=0, verticalalignment="center",
    arrowprops=dict(arrowstyle="-", linewidth=.5),
    bbox=dict(boxstyle="square,pad=0.2", linewidth=0,
        facecolor="white", edgecolor="black")
)

autopct = lambda pct: f"{pct:.0f}%"

FIGSIZE = (2, 1.6)


#### Draw

fig, ax = plt.subplots(figsize=FIGSIZE, constrained_layout=True)

wedges, texts, autotexts = ax.pie(sizes,
    colors=colors, labels=labels, explode=None, autopct=autopct,
    wedgeprops=PIE_WEDGE_KWARGS, textprops=PIE_TEXT_KWARGS,
    **PIE_KWARGS)

ax.axis("equal")

#### Put a few labels outside the pie chart.

for wedge_id, wedge_patch, text in zip(WEDGE_ORDER, wedges, texts):
    if wedge_id in ["pos", "neg"]:
        text.set_text("") # clear original label
        ang = (wedge_patch.theta2-wedge_patch.theta1)/2 + wedge_patch.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        l = wedge_patch.get_label()
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = f"angle,angleA=0,angleB={ang}"
        ANNOTATE_KWARGS["arrowprops"]["connectionstyle"] = connectionstyle
        ax.annotate(l, xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
            horizontalalignment=horizontalalignment, **ANNOTATE_KWARGS)

    # Make more subtle adjustments to others.
    elif wedge_id == "total":
        x, y = text.get_position()
        x -= .1
        y -= .1
        text.set_position((x, y))

ax.set_title(title)


# Export.
plt.savefig(export_fullpath)
utils.save_hires_copies(export_fullpath)
plt.close()