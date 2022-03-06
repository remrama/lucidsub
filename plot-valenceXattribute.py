"""Plot the chi2 results from attribute-rating analysis.
Mosaic plots using statsmodels.
"""
import os
import argparse
import pandas as pd
import utils

from distutils.util import strtobool

from statsmodels.graphics.mosaicplot import mosaic
import matplotlib.pyplot as plt
utils.load_matplotlib_settings()


parser = argparse.ArgumentParser()
parser.add_argument("-a", "--attribute", type=str, default="control", choices=["control", "lucidity"])
parser.add_argument("--drawcounts", action="store_true", help="Draw expected and observed in mosaic cells. Good to make sure they overlap with chi2 Pingouin output.")
args = parser.parse_args()


DRAW_COUNTS = args.drawcounts
ATTRIBUTE = args.attribute


############### I/O and loading data.

export_basename = f"themes-valenceXattribute_{ATTRIBUTE}.png"
export_fullpath = os.path.join(utils.Config.data_directory, "results", export_basename)

import_basename = "themes-valenceXattribute_freqs.csv"
import_fullpath = os.path.join(utils.Config.data_directory, "results", import_basename)

import_fullpath_stats = import_fullpath.replace("_freqs.csv", "_stats.csv")


df = pd.read_csv(import_fullpath, index_col="attribute")
stats_df = pd.read_csv(import_fullpath_stats, index_col=["attribute", "test"])


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


# Get stats values
chi2val, pval = stats_df.loc[(ATTRIBUTE,"pearson"), ["chi2", "pval"]]


############### Plotting variables.

FIGSIZE = (2.2, 1.8)
w2h_ratio = FIGSIZE[0] / FIGSIZE[1]
AX_LEFT = .26
AX_WIDTH = .42
AX_TOP = .75
ax_height = AX_WIDTH*w2h_ratio
GRIDSPEC_KW = dict(left=AX_LEFT, right=AX_LEFT+AX_WIDTH,
    top=AX_TOP, bottom=AX_TOP-ax_height)

SIG_XLOC = 1.05
SIG_YLOC = .5

palette = utils.load_config(as_object=False)["colors"]

PROPS = lambda key: { # ("True", "True") strings(?) tuple in key_order
    "color": palette[key[1]], "alpha": 1,
}

def labelizer(key):
    """Determines what is drawn, if anything, in the boxes.
    """
    if DRAW_COUNTS:
        # Mosaic turns boolean to string, have to get them back for indexing
        key = tuple([ bool(strtobool(k)) if k in ("True", "False") else k for k in key ])
        # expected_count = ser.loc[key, "expected"]
        observed_count = ser.loc[key]
        return f"Observed\n{observed_count}"
    else:
        return None


############### Draw.

# Open figure.
fig, ax = plt.subplots(figsize=FIGSIZE, gridspec_kw=GRIDSPEC_KW)

# Draw boxes.
_, rects = mosaic(data=ser, properties=PROPS,
    labelizer=labelizer, horizontal=True,
    axes_label=True, gap=.05, ax=ax)

# Adjustments.
ax.set_xlabel(xlabel)
ax.set_xticklabels(var_order)
ax.set_ylabel("Relative frequency", labelpad=2)
ax.yaxis.set(major_locator=plt.MultipleLocator(.5),
    minor_locator=plt.MultipleLocator(.1),
    major_formatter=plt.matplotlib.ticker.PercentFormatter(xmax=1))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_position(("outward", 5))
ax.spines["bottom"].set_position(("outward", 5))

ax2 = ax.twiny()
ax2.spines["top"].set_position(("outward", 5))
ax2.set_xlabel("Relative frequency", labelpad=6)
ax2.xaxis.set(major_locator=plt.MultipleLocator(.5),
    minor_locator=plt.MultipleLocator(.1),
    major_formatter=plt.matplotlib.ticker.PercentFormatter(xmax=1))

# ax.tick_params(left=False, bottom=False)
# for ch in ax.get_children():
#     if isinstance(ch, plt.Text):
#         ch.set_horizontalalignment("left")

handles = [ plt.matplotlib.patches.Patch(
        edgecolor="none", facecolor=c, label=l)
    for l, c in palette.items() ]
legend = ax.legend(handles=handles,
    title="Post valence",
    loc="upper left", bbox_to_anchor=(1, 1), borderaxespad=0,
    frameon=False, labelspacing=.1, handletextpad=.2)
# legend._legend_box.sep = 2 # brings title up farther on top of handles/labels
legend._legend_box.align = "left"


# Add significance text.
sigchars = "*" * sum([ pval<cutoff for cutoff in (.05, .01, .001) ])
ptxt = r"p<0.001" if pval < .001 else fr"$p={pval:.2f}$"
ptxt = ptxt.replace("0", "", 1)
chi2txt = fr"$\chi^2={chi2val:.0f}$"
stats_txt = chi2txt + "\n" + ptxt + sigchars
ax.text(SIG_XLOC, SIG_YLOC, stats_txt, transform=ax.transAxes,
    ha="left", va="top", linespacing=1)

# Export!
plt.savefig(export_fullpath)
utils.save_hires_copies(export_fullpath)
plt.close()
