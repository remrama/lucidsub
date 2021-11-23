"""
analyze the control ratings.
plot.
"""
import os
import pandas as pd
import pingouin as pg

import config as c

from statsmodels.graphics.mosaicplot import mosaic
import matplotlib.pyplot as plt
plt.rcParams["savefig.dpi"] = 600
plt.rcParams["interactive"] = True
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Arial"

import_fname1 = os.path.join(c.DATA_DIR, "doccano-20211110", "lsowin.csv")
import_fname2 = os.path.join(c.RESULTS_DIR, "themes-highlights_table.csv")
export_fname_plot = os.path.join(c.RESULTS_DIR, "plots", "valenceXcontrol.png")
export_fname_chi2E = os.path.join(c.RESULTS_DIR, "valenceXcontrol_chi2-expected.csv")
export_fname_chi2O = os.path.join(c.RESULTS_DIR, "valenceXcontrol_chi2-observed.csv")
export_fname_chi2S = os.path.join(c.RESULTS_DIR, "valenceXcontrol_chi2-stats.csv")

# load in data
ser1 = pd.read_csv(import_fname1, usecols=[0,2],
        index_col="id", squeeze=True
    ).replace(
        {
            "not a dream" : pd.NA,
            "no control" : False,
            "yes control" : True
        }
    ).rename("control"
    ).rename_axis("post_id"
    ).dropna(
    ).astype(bool)

# all this junk gets down to only the posts with just neg
# or just pos themes (doesn't care how many themes within pos or neg)
ser2 = pd.read_csv(import_fname2, usecols=[0,1],
        index_col="post_id", squeeze=True
    ).replace(c.POS_THEMES, True
    ).replace(c.NEG_THEMES, False
    ).rename("positive"
    ).reset_index(
        ).drop_duplicates(subset=None, # drop duplicated pos or neg within post
        ).drop_duplicates(subset="post_id", keep=False # drop all posts with pos and neg
        ).set_index("post_id"
        ).squeeze()

df = pd.concat([ser1, ser2], axis=1, join="inner")
# pd.merge(ser1, ser2, how="left", left_index=True, right_index=
#     ...: True, validate="1:1")

# stats
expected, observed, stats = pg.chi2_independence(
    df, x="control", y="positive", correction=False)

# export stats
expected.to_csv(export_fname_chi2E, index=True)
observed.to_csv(export_fname_chi2O, index=True)
stats.to_csv(export_fname_chi2S, index=False)


#### plot

key_order = ["control", "positive"]

props = lambda key: { # ("True", "True") strings(?) tuple in key_order
    # "color": c.POS_COLOR if key[1]=="True" else c.NEG_COLOR,
    # "alpha": 1 if key[0]=="True" else .5,
    "color": "gainsboro",
    "alpha": 1,
}
# props = lambda key: {
#     "color": "gray",
#     "alpha": 1,
# }
def labelizer(key):
    # stupid get bools to strings
    a, b = [ False if k=="False" else True for k in key ]
    expected_count = expected.loc[a, b]
    observed_count = observed.loc[a, b]
    box_txt = f"Expected: {expected_count}\nObserved: {observed_count}"
    return box_txt
# labelizer = lambda key: None
gridspec_kw = dict(top=.98, right=.98, bottom=.22, left=.22)
fig, ax = plt.subplots(figsize=(4,4),
    gridspec_kw=gridspec_kw)
fig, rects = mosaic(
    df.sort_values(key_order),
    key_order,
    ax=ax,
    properties=props,
    # statistic=True,
    gap=.05,
    axes_label=True,
    labelizer=labelizer)
# ax.set_xlabel(key_order[0])
# ax.set_ylabel(key_order[1])


control_labels = ["Little to no\ndream control", "High\ndream control"]
theme_labels = ["Negative\ntheme post", "Positive\ntheme post"]
if key_order[0] == "control":
    ax.set_xticklabels(control_labels)
    ax.set_yticklabels(theme_labels)
else:
    ax.set_xticklabels(theme_labels)
    ax.set_yticklabels(control_labels)

for ax in fig.get_axes():
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_position(("outward", 5))
    ax.spines["bottom"].set_position(("outward", 5))
    # ax.tick_params(left=False, bottom=False)
    # for ch in ax.get_children():
    #     if isinstance(ch, plt.Text):
    #         ch.set_horizontalalignment("left")


# export plot
plt.savefig(export_fname_plot)
plt.close()
