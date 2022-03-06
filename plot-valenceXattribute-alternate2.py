"""A pie chart version.

!!!!!!!!!!!! This is totally sloppy and does NOT generate anything important.
!!!!!!!!!!!! Use/reuse with caution.
"""
import os
import argparse
import numpy as np
import pandas as pd
import utils

import matplotlib.pyplot as plt
utils.load_matplotlib_settings()


parser = argparse.ArgumentParser()
parser.add_argument("-a", "--attribute", type=str, default="control", choices=["control", "lucidity"])
parser.add_argument("--drawcounts", action="store_true", help="Draw expected and observed in mosaic cells. Good to make sure they overlap with chi2 Pingouin output.")
args = parser.parse_args()


DRAW_COUNTS = args.drawcounts
ATTRIBUTE = args.attribute


############### I/O and loading data.

export_basename = f"themes-valenceXattribute_{ATTRIBUTE}-alternate2.png"
export_fullpath = os.path.join(utils.Config.data_directory, "results", export_basename)

import_basename = "themes-valenceXattribute_freqs.csv"
import_fullpath = os.path.join(utils.Config.data_directory, "results", import_basename)


df = pd.read_csv(import_fullpath, index_col="attribute")

# Restructure data for mosaic plot.
df = df.loc[ATTRIBUTE, ["valence", "present", "observed"]]

# Replace values for ordering and ticks.
if ATTRIBUTE == "control":
    var_order = ["low", "high"]
    xlabel = "Dream control"
elif ATTRIBUTE == "lucidity":
    var_order = ["no", "yes"]
    xlabel = "Attained lucidity"
df = df.rename(columns=dict(present=ATTRIBUTE))

replacements = { k: v for k, v in zip([False, True], var_order) }
df[ATTRIBUTE] = df[ATTRIBUTE].replace(replacements)

# ser = df.set_index([ATTRIBUTE, "valence"]
#     ).squeeze( # needs to be series for mosaic to acknowledge counts
#     ).sort_index()

c = ["gainsboro", "gainsboro"]
palette = { k:v for k, v in zip(var_order, c) }
# palette = utils.load_config(as_object=False)["colors"]

valence_order = ["positive", "negative"][::-1]

FIGSIZE = (3, 2)
GRIDSPEC_KWARGS = dict(wspace=.01, hspace=.1,
    width_ratios=[1.5, 1.2, 1.5],
    height_ratios=[1.5, 1],
    top=.8, left=.02, right=.98, bottom=0)

fig = plt.figure(figsize=FIGSIZE)
gs = plt.matplotlib.gridspec.GridSpec(
    nrows=2, ncols=3, **GRIDSPEC_KWARGS)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[:, 1])
ax3 = fig.add_subplot(gs[0, 2])
# fig, (ax1, ax2, ax3) = plt.subplots(ncols=3,
#     figsize=FIGSIZE, gridspec_kw=GRIDSPEC_KWARGS,
#     constrained_layout=False)


pie_slices = df.groupby(ATTRIBUTE)["observed"].sum()[::-1].to_dict()
# pie_slices = df.groupby("valence")["observed"].sum().to_dict()
labels, sizes = zip(*pie_slices.items())
colors = [ palette[x] for x in pie_slices.keys() ]
# colors = [ cc.cm.glasbey_dark(i) for i in range(len(pie_slices)) ]
explode = [.15, .15]
wedges, texts, autotexts = ax2.pie(sizes,
    labels=labels, colors=colors, explode=explode,
    autopct=lambda pct: f"{pct:.0f}%",
    shadow=False, startangle=90,
    labeldistance=.3, rotatelabels=False,
    pctdistance=.5,
    textprops=dict(color="black"),
    wedgeprops=dict(linewidth=.5))
ax2.axis("equal") # ensure pie is drawn as a circle
# ax2.set_title(xlabel, y=.9, va="top")
# ax2.text(.5, .7, xlabel, transform=ax2.transAxes, va="bottom", ha="center")
ax2.text(.5, .2, xlabel, transform=ax2.transAxes, va="bottom", ha="center")
for i, t in enumerate(texts):
    x, y = t.get_position()
    if i==0: y += .4
    else: y -= .4
    t.set_position((x, y))


vpal = utils.load_config(as_object=False)["colors"]
# for v, vdf in df.groupby("valence"):
for v, vdf in df.groupby(ATTRIBUTE):
    # ax = ax1 if v=="negative" else ax3
    ax = ax1 if v=="low" else ax3
    # sizes = vdf.set_index(ATTRIBUTE).loc[var_order, "observed"].values
    sizes = vdf.set_index("valence").loc[valence_order, "observed"].values
    colors = [ vpal[v] for v in valence_order ]
    # colors = (palette[v],) *2
    alphas = [.2, 1]
    sangle = 0 if v == "high" else 180
    # sangle = 90
    explode = [.1, .1]
    explode = None
    labeldistance = .1
    pctdistance = .6
    # labeldistance = .78
    # pctdistance = .45
    wedges, texts, autotexts = ax.pie(sizes,
        labels=valence_order, colors=colors,
        autopct=lambda pct: f"{pct:.0f}%",
        shadow=False, explode=explode, startangle=sangle,
        labeldistance=labeldistance, rotatelabels=False,
        pctdistance=pctdistance,
        textprops=dict(color="black"),
        wedgeprops=dict(linewidth=.5))
    ax.axis("equal") # ensure pie is drawn as a circle
    # for a, w in zip(alphas, wedges):
    #     w.set_alpha(a)
    if v == "high":
        for i, t in enumerate(autotexts):
            x, y = t.get_position()
            if i==0: y += .1
            else: y -= .1
            t.set_position((x, y))

    # label = f"{xlabel}\nin {v} posts"
    label = f"Valence in {v}\n{xlabel.lower()} posts"
    ax.set_xlabel(label)


SIG_YLOC = 1.1
SIG_YHEIGHT = .04
LINE_KWARGS = dict(color="black", linewidth=1, alpha=1, clip_on=False)

con = plt.matplotlib.patches.ConnectionPatch(
    xyA=(.5, SIG_YLOC), coordsA=ax1.transAxes,
    xyB=(.5, SIG_YLOC), coordsB=ax3.transAxes,
    **LINE_KWARGS)
ax1.add_artist(con)

ax1.axvline(x=0, ymin=SIG_YLOC-SIG_YHEIGHT, ymax=SIG_YLOC,
    solid_capstyle="round", **LINE_KWARGS)
ax3.axvline(x=0, ymin=SIG_YLOC-SIG_YHEIGHT, ymax=SIG_YLOC,
    solid_capstyle="round", **LINE_KWARGS)

ax2.text(.5, SIG_YLOC-.03, "***", transform=ax2.transAxes,
    horizontalalignment="center", verticalalignment="bottom",
    fontsize=12)


# xmin, xmax = xvals[2*xindx:2*xindx+2]
# xtxt = xvals[2*xindx:2*xindx+2].mean()
# ax.hlines(y=ytxt, xmin=xmin, xmax=xmax,
#     linewidth=1, color=sigcolor(pval), capstyle="round",
#     transform=ax.get_xaxis_transform())

plt.savefig(export_fullpath)
plt.close()