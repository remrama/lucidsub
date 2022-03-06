"""Another pie chart version.

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

export_basename = f"themes-valenceXattribute_{ATTRIBUTE}-alternate3.png"
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
    var_order = ["low", "yes"]
    xlabel = "Attained lucidity"
df = df.rename(columns=dict(present=ATTRIBUTE))

replacements = { k: v for k, v in zip([False, True], var_order) }
df[ATTRIBUTE] = df[ATTRIBUTE].replace(replacements)

# ser = df.set_index([ATTRIBUTE, "valence"]
#     ).squeeze( # needs to be series for mosaic to acknowledge counts
#     ).sort_index()


###################### Pie chart version


FIGSIZE = (3, 2)
GRIDSPEC_KWARGS = dict(wspace=.5,
    width_ratios=[1, 3, 1],
    left=.2, right=.98, top=.85, bottom=.06)

fig, axes = plt.subplots(ncols=3,
    figsize=FIGSIZE,
    gridspec_kw=GRIDSPEC_KWARGS,
    constrained_layout=False)


################### Pie

c = ["gainsboro", "darkgray"]
c = ["whitesmoke", "whitesmoke"]
palette = { k:v for k, v in zip(var_order, c) }
pie_slices = df.groupby(ATTRIBUTE)["observed"].sum()[::-1].to_dict()
# palette = utils.load_config(as_object=False)["colors"]
# pie_slices = df.groupby("valence")["observed"].sum().to_dict()

labels, sizes = zip(*pie_slices.items())
explode = [ .1, .1 ]
colors = [ palette[x] for x in pie_slices.keys() ]
# colors = [ cc.cm.glasbey_dark(i) for i in range(len(pie_slices)) ]
wedges, texts, autotexts = axes[1].pie(sizes,
    labels=labels, colors=colors,
    autopct=lambda pct: f"{pct:.0f}%",
    shadow=False, explode=explode, startangle=90,
    labeldistance=.2, rotatelabels=False,
    pctdistance=.3,
    textprops=dict(color="black"),
    wedgeprops=dict(linewidth=.5, edgecolor="black"))
axes[1].axis("equal") # ensure pie is drawn as a circle

# for innertxt, outertxt in zip(texts, autotexts):
for i, t in enumerate(texts):
    # label = t.get_label()
    x, y = t.get_position()
    if i == 0:
        y += .3
    else:
        y -= .3
    t.set_position((x, y))

################### Bar

BAR_WIDTH = .001

valence_order = ["positive", "negative"][::-1]

def draw_valence_bar(valence, ax):

    # bar_heights = df.query(f"valence=='{valence}'"
    #     ).set_index(ATTRIBUTE).loc[var_order, "observed"].to_dict()
    bar_heights = df.query(f"{ATTRIBUTE}=='{valence}'"
        ).set_index("valence").loc[valence_order, "observed"].to_dict()

    xpos = 0
    bottom = 0
    n_segments = len(bar_heights)
    labels, heights = zip(*bar_heights.items())

    # color = palette[valence]
    # colors = ["mediumpurple", "blueviolet"]
    # colors = [ cc.cm.glasbey_dark(i) for i in range(len(bar_segments)) ]
    # colors = ["darkgray", "mediumpurple"]
    # colors = ["#a89008", "#3a90fe"]
    # colors = ["#719083", "#3a90fe"]
    # colors = ["white", "gray"]
    colors = [ utils.load_config(as_object=False)["colors"][c] for c in valence_order ]
    alphas = [1, 1]

    for i in range(n_segments):
        height = heights[i]
        label = labels[i]
        alpha = alphas[i]
        color = colors[i]
        # color = palette[valence]
        ax.bar(xpos, height, BAR_WIDTH,
            bottom=bottom, alpha=alpha, color=color,
            clip_on=False)
        label_ypos = bottom + ax.patches[i].get_height() / 2
        bottom += height
        # label_txt = "%d%%" % (ax3.patches[j].get_height() * 100)
        label_txt = str(height) + " " + label
        # ax.text(xpos, label_ypos, label_txt, ha="center")

    # ax2.set_title('Age of approvers')
    # ax2.legend(('50-65', 'Over 65', '35-49', 'Under 35'))
    # ax.axis("off")
    # ax.set_xlim(-2.5*BAR_WIDTH, 2.5*BAR_WIDTH)
    ax.set_xlim(-BAR_WIDTH/2, BAR_WIDTH/2)
    ax.set_ybound(upper=bottom)
    # for spine in ax.spines.values():
    #     spine.set_edgecolor(palette[valence])
    # ax.spines["top"].set_visible(False)
    # ax.spines["bottom"].set_visible(False)
    if valence == "low":
        major_formatter = plt.matplotlib.ticker.PercentFormatter(xmax=bottom)
        ax.set_ylabel("Relative frequency", labelpad=1)
        ax.tick_params(direction="in", labelbottom=False, bottom=False)
        # ax.spines["right"].set_visible(False)
    else:
        ax.tick_params(direction="in", labelbottom=False, bottom=False)#, left=False, right=True)
        major_formatter = plt.NullFormatter()
        # ax.spines["left"].set_visible(False)
    ax.yaxis.set(major_locator=plt.MultipleLocator(bottom/4),
        # minor_locator=plt.MultipleLocator(.1),
        major_formatter=major_formatter)
    # ax.spines["left"].set_position(("outward", 5))
    # ax.spines["bottom"].set_position(("outward", 5))

def draw_connecting_lines(wedge, pie_ax, bar_ax, side,
    color="black", linewidth=.5, alpha=.1):

    # get the wedge data
    theta1, theta2 = wedge.theta1, wedge.theta2
    center, r = wedge.center, wedge.r
    bar_height = sum([ p.get_height() for p in bar_ax.patches ])

    # draw top connecting line
    t = theta2 if side == "right" else theta1
    x = r * np.cos(np.pi / 180 * t) + center[0]
    y = r * np.sin(np.pi / 180 * t) + center[1]
    xA = -BAR_WIDTH/2 if side=="right" else BAR_WIDTH/2
    con = plt.matplotlib.patches.ConnectionPatch(
        xyA=(xA, bar_height), coordsA=bar_ax.transData,
        xyB=(x, y), coordsB=pie_ax.transData)
    con.set_color(color)
    con.set_alpha(alpha)
    con.set_linewidth(linewidth)
    bar_ax.add_artist(con)

    # draw bottom connecting line
    t = theta1 if side == "right" else theta2
    x = r * np.cos(np.pi / 180 * t) + center[0]
    y = r * np.sin(np.pi / 180 * t) + center[1]
    con = plt.matplotlib.patches.ConnectionPatch(
        xyA=(xA, 0), coordsA=bar_ax.transData,
        xyB=(x, y), coordsB=pie_ax.transData)
    con.set_color(color)
    con.set_alpha(alpha)
    con.set_linewidth(linewidth)
    bar_ax.add_artist(con)


for v, bax in zip(pie_slices.keys(), axes[::2]):
    draw_valence_bar(v, bax)

for wedge, side, bax in zip(axes[1].patches, ["left", "right"], axes[::2]):
    draw_connecting_lines(wedge, axes[1], bax, side=side)

n = sum(pie_slices.values())
if ATTRIBUTE == "control":
    title = f"{n} dream posts"
elif ATTRIBUTE == "lucidity":
    title = f"{n} posts"
title += " with\nsingular valence"
axes[1].set_title(xlabel, y=.9, va="top")



SIG_YLOC = 1.1
SIG_YHEIGHT = .04
LINE_KWARGS = dict(color="black", linewidth=1, alpha=1, clip_on=False)

con = plt.matplotlib.patches.ConnectionPatch(
    xyA=(.5, SIG_YLOC), coordsA=axes[0].transAxes,
    xyB=(.5, SIG_YLOC), coordsB=axes[2].transAxes,
    **LINE_KWARGS)
axes[0].add_artist(con)

for ax in axes[::2]:
    ax.axvline(x=0, ymin=SIG_YLOC-SIG_YHEIGHT,
        ymax=SIG_YLOC, solid_capstyle="round", **LINE_KWARGS)

axes[1].text(.5, SIG_YLOC-.03, "***", transform=axes[1].transAxes,
    horizontalalignment="center", verticalalignment="bottom",
    fontsize=12)

# lcolors = ["white", "gray"]
vpalette = utils.load_config(as_object=False)["colors"]
handles = [ plt.matplotlib.patches.Patch(
        edgecolor="black", linewidth=.3,
        facecolor=c, label=l)
    for l, c in vpalette.items() ]
    # for c, l in zip(lcolors, var_order) ]
LEGEND_KWARGS = dict(borderaxespad=0,
    loc="center", bbox_to_anchor=(.5, 0),
    ncol=2, columnspacing=1,
    frameon=False, labelspacing=.1, handletextpad=.2)
legend = axes[1].legend(handles=handles,
    title="valence", **LEGEND_KWARGS)
# legend._legend_box.sep = 2 # brings title up farther on top of handles/labels
# legend._legend_box.align = "left"



plt.savefig(export_fullpath)
plt.close()