"""Plot the chi2 results from attribute-rating analysis.
Mosaic plots using statsmodels.
"""
import os
import argparse
import pandas as pd
import utils

from distutils.util import strtobool

import statsmodels.api as sm
from statsmodels.graphics.mosaicplot import mosaic
import matplotlib.pyplot as plt
utils.load_matplotlib_settings()


parser = argparse.ArgumentParser()
parser.add_argument("-a", "--attribute", type=str, choices=["control", "lucidity"])
parser.add_argument("--drawcounts", action="store_true", help="Draw expected and observed in mosaic cells. Good to make sure they overlap with chi2 Pingouin output.")
args = parser.parse_args()


DRAW_COUNTS = args.drawcounts
ATTRIBUTE = args.attribute


############### I/O and loading data.

export_basename = f"themes-valenceXattribute_{ATTRIBUTE}.png"
export_fullpath = os.path.join(utils.Config.data_directory, "results", export_basename)

import_basename = "themes-valenceXattribute_freqs.csv"
import_fullpath = os.path.join(utils.Config.data_directory, "results", import_basename)

df = pd.read_csv(import_fullpath, index_col="attribute")

# Restructure data for mosaic plot.
df = df.loc[ATTRIBUTE, ["valence", "present", "observed"]]
df = df.rename(columns=dict(present=ATTRIBUTE))
ser = df.set_index(["valence", ATTRIBUTE]
    ).squeeze( # needs to be series for mosaic to acknowledge counts
    ).sort_index(ascending=[False, True]) # flip so positive is first on x axis


############### Plotting variables.

FIGSIZE = (2, 2)
GRIDSPEC_KW = dict(left=.3, right=.99, bottom=.3, top=.99)

if ATTRIBUTE == "control":
    tick_labels = ["little\nor\nnone", "high"]
    axis_label = "Dream control"
elif ATTRIBUTE == "lucidity":
    tick_labels = ["no", "yes"]
    axis_label = "Attained lucidity"

PROPS = lambda key: { # ("True", "True") strings(?) tuple in key_order
    "color": utils.Config.colors.negative if key[0]=="negative" else utils.Config.colors.positive,
    # "alpha": 1 if key[0]=="True" else .5,
    # "color": "gainsboro",
    "alpha": 1,
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

# Open figure
fig, ax = plt.subplots(figsize=FIGSIZE, gridspec_kw=GRIDSPEC_KW)

# Draw boxes.
_, rects = mosaic(data=ser, properties=PROPS,
    labelizer=labelizer, horizontal=True,
    axes_label=True, gap=.05, ax=ax)

# Adjustments.
ax.set_xlabel("Post valence")
ax.set_xticklabels(["positive", "negative"])
ax.set_ylabel(axis_label)
ax.set_yticklabels(tick_labels)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_position(("outward", 5))
ax.spines["bottom"].set_position(("outward", 5))
# ax.tick_params(left=False, bottom=False)
# for ch in ax.get_children():
#     if isinstance(ch, plt.Text):
#         ch.set_horizontalalignment("left")


# Export!
plt.savefig(export_fullpath)
utils.save_hires_copies(export_fullpath)
plt.close()
