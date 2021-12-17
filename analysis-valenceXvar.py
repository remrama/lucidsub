"""
analyze how the extra dimensions relate to valence.

export the stats tables separately but plot them together
(stupid loop for that reason)
"""
import os
import argparse
import pandas as pd
import config as c

import pingouin as pg
import statsmodels.api as sm

from statsmodels.graphics.mosaicplot import mosaic
import matplotlib.pyplot as plt
plt.rcParams["savefig.dpi"] = 600
plt.rcParams["interactive"] = True
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Arial"


parser = argparse.ArgumentParser()
parser.add_argument("--drawcounts", action="store_true")
args = parser.parse_args()

DRAW_COUNTS = args.drawcounts # draw expected and observed in mosaic cells

props = lambda key: { # ("True", "True") strings(?) tuple in key_order
    "color": c.NEG_COLOR if key[0]=="True" else c.POS_COLOR,
    # "alpha": 1 if key[0]=="True" else .5,
    # "color": "gainsboro",
    "alpha": 1,
}
# props = lambda key: {
#     "color": "gray",
#     "alpha": 1,
# }
def labelizer(key):
    # stupid get bools to strings
    a, b = [ False if k=="False" else True for k in key ]
    expected_count = freqs.loc[(a,b), "expected"]
    observed_count = freqs.loc[(a,b), "observed"]
    box_txt = f"Expected: {expected_count}\nObserved: {observed_count}"
    return box_txt if DRAW_COUNTS else ""
# labelizer = lambda key: None

GRIDSPEC_KW = dict(wspace=.7, left=.15, right=.98, bottom=.25, top=.98)
FIGSIZE = (5, 2)
fig, axes = plt.subplots(ncols=2, figsize=FIGSIZE,
    sharex=False, sharey=False, gridspec_kw=GRIDSPEC_KW)
fig.text(0, 1, "A", fontsize=12, fontweight="bold", ha="left", va="top")
fig.text(.5, 1, "B", fontsize=12, fontweight="bold", ha="left", va="top")
# fig = plt.figure(constrained_layout=True)
# subfigs = fig.subfigures(ncols=2, wspace=0.07)
# ax1 = subfigs[0].subplots()
# ax2 = subfigs[1].subplots()
# axes = [ax1, ax2]

export_fname_plot = os.path.join(c.RESULTS_DIR, "plots", "valenceXvar.png")



for ax, VAR in zip(axes, ["ldexp", "control"]):


    ##### do the numbers
    if VAR == "control":
        import_fname1 = os.path.join(c.DATA_DIR, "doccano-20211110", "lsowin.csv")
    elif VAR == "ldexp":
        import_fname1 = os.path.join(c.DATA_DIR, "doccano-20211123", "lsowin.csv")
    import_fname2 = os.path.join(c.RESULTS_DIR, "themes-highlights_table.csv")
    export_fname_freq = os.path.join(c.RESULTS_DIR, f"valenceX{VAR}_chi2-freq.csv")
    export_fname_stat = os.path.join(c.RESULTS_DIR, f"valenceX{VAR}_chi2-stat.csv")

    # load in data
    ser1 = pd.read_csv(import_fname1, usecols=[0,2], index_col="id", squeeze=True)

    key_order = ["negative", VAR]
    VALENCE_AX_LABEL = "Post valence"
    VALENCE_TICK_LABELS = ["positive", "negative"]

    if VAR == "control":
        TICK_LABELS = ["little\nor\nnone", "high"]
        AX_LABEL = "Dream control"
        ser1 = ser1.replace(
                {
                    "not a dream" : pd.NA,
                    "no control" : False,
                    "yes control" : True
                }
            )
    elif VAR == "ldexp":
        TICK_LABELS = ["no", "yes"]
        AX_LABEL = "Attained lucidity"
        ser1 = ser1.replace(
                {
                    "not an LD" : False,
                    "LD" : True,
                }
            )

    ser1 = ser1.rename(VAR
        ).rename_axis("post_id"
        ).dropna(
        ).astype(bool)



    # all this junk gets down to only the posts with just neg
    # or just pos themes (doesn't care how many themes within pos or neg)
    ser2 = pd.read_csv(import_fname2, usecols=[0,1],
            index_col="post_id", squeeze=True
        ).replace(c.POS_THEMES, False
        ).replace(c.NEG_THEMES, True
        ).rename("negative"
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
        df, x=key_order[0], y=key_order[1], correction=False)

    # use statsmodels to get residuals
    # https://stackoverflow.com/a/20457483
    sm_table = sm.stats.Table(observed)
    # # sm_table.fittedvalues # this is same as expected from pingouin

    # merge expected and observed into one dataframe for exporting
    freqs = pd.concat([
            expected.unstack().rename("expected"),
            observed.unstack().rename("observed"),
            sm_table.resid_pearson.unstack().rename("res"),
            sm_table.standardized_resids.unstack().rename("stdres"),
        ], axis=1
        ).round(1
        ).reorder_levels(key_order)

    # export stats
    freqs.to_csv(export_fname_freq, index=True)
    stats.to_csv(export_fname_stat, index=False)


    ################### plot


    _, rects = mosaic(
        data=df.sort_values(key_order),
        index=key_order,
        horizontal=True,
        ax=ax,
        properties=props,
        # statistic=True,
        gap=.05,
        axes_label=True,
        labelizer=labelizer,
    )

    if key_order[0] == "negative": # valence on x axis
        ax.set_xlabel(VALENCE_AX_LABEL, fontsize=10)
        ax.set_ylabel(AX_LABEL, fontsize=10)
        ax.set_xticklabels(VALENCE_TICK_LABELS, fontsize=10)
        ax.set_yticklabels(TICK_LABELS, fontsize=10)
    else:
        ax.set_xlabel(AX_LABEL, fontsize=10)
        ax.set_ylabel(VALENCE_AX_LABEL, fontsize=10)
        ax.set_xticklabels(TICK_LABELS, fontsize=10)
        ax.set_yticklabels(VALENCE_TICK_LABELS, fontsize=10)

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
