"""Plot the chi2 results from attribute-rating analysis.
WITHOUT mosaic plot. Benefit is the gap in x axis.

!!!!!!!!!!!! This is totally sloppy and does NOT generate anything important.
!!!!!!!!!!!! Use/reuse with caution.
"""
import os
import argparse
import pandas as pd
import utils

from distutils.util import strtobool

import matplotlib.pyplot as plt
utils.load_matplotlib_settings()


parser = argparse.ArgumentParser()
parser.add_argument("-a", "--attribute", type=str, default="control", choices=["control", "lucidity"])
parser.add_argument("--drawcounts", action="store_true", help="Draw expected and observed in mosaic cells. Good to make sure they overlap with chi2 Pingouin output.")
args = parser.parse_args()


DRAW_COUNTS = args.drawcounts
ATTRIBUTE = args.attribute


############### I/O and loading data.

export_basename = f"themes-valenceXattribute_{ATTRIBUTE}-alternate1.png"
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

ser = df.set_index([ATTRIBUTE, "valence"]
    ).squeeze( # needs to be series for mosaic to acknowledge counts
    ).sort_index()

# replacements = { k: v for k, v in zip([False, True], var_order) }
# df[ATTRIBUTE] = df[ATTRIBUTE].replace(replacements)


############### Plotting variables.

FIGSIZE = (2.2, 1.5)
w2h_ratio = FIGSIZE[0] / FIGSIZE[1]
AX_LEFT = .26
AX_WIDTH = .42
AX_TOP = .97
ax_height = AX_WIDTH*w2h_ratio
width_ratios = ser.groupby(ATTRIBUTE).sum().values
WSPACE = .1
GRIDSPEC_KW = dict(wspace=WSPACE,
    left=AX_LEFT, right=AX_LEFT+AX_WIDTH,
    top=AX_TOP, bottom=AX_TOP-ax_height,
    width_ratios=width_ratios)

palette = utils.load_config(as_object=False)["colors"]

# Open figure.
fig, (ax1, ax2) = plt.subplots(ncols=2,
    figsize=FIGSIZE, gridspec_kw=GRIDSPEC_KW)

ax2.tick_params(left=False, labelleft=False)
ax1.spines["left"].set_position(("outward", 3))
ax1.spines["bottom"].set_position(("outward", 3))
ax2.spines["bottom"].set_position(("outward", 3))
ax2.spines["top"].set_visible(False)
ax2.spines["left"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)


############### Draw.

BAR_KWARGS = dict(width=1,
    edgecolor="black", linewidth=0, clip_on=False)

valence_order = ["negative", "positive"]
table = ser.unstack()
for attr, row in table.iterrows():
    ax = ax1 if attr==False else ax2
    bottom = 0
    for v in valence_order:
        height = row.loc[v]
        color = palette[v]
        ax.bar(0, height, bottom=bottom, color=color, **BAR_KWARGS)
        bottom += height
    ax.set_ybound(upper=bottom)
    ax.set_xlim(-.5, .5)
    ax.set_xticks([0])
    label = var_order[0] if attr==False else var_order[1]
    ax.set_xticklabels([label])

    if attr == False:
        ax.set_ylabel("Relative frequency", labelpad=2)
        ax.yaxis.set(major_locator=plt.MultipleLocator(bottom/4),
            # minor_locator=plt.MultipleLocator(.1),
            major_formatter=plt.matplotlib.ticker.PercentFormatter(xmax=bottom))

handles = [ plt.matplotlib.patches.Patch(
        edgecolor="none", facecolor=c, label=l)
    for l, c in palette.items() ]
legend = ax.legend(handles=handles,
    title="Post valence",
    loc="upper left", bbox_to_anchor=(1, 1), borderaxespad=0,
    frameon=False, labelspacing=.1, handletextpad=.2)
# legend._legend_box.sep = 2 # brings title up farther on top of handles/labels
legend._legend_box.align = "left"


fig.text(.3, .1, xlabel)


fig.align_labels()

plt.savefig(export_fullpath)
plt.close()