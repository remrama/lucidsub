"""
exploring inter-rater reliability
"""
import os
import json
import string
import random

import numpy as np
import pandas as pd

import pingouin as pg
import krippendorff
from sklearn.metrics import cohen_kappa_score
from statsmodels.stats import inter_rater

import itertools
from random import shuffle

import matplotlib.pyplot as plt; plt.ion()

plt.rcParams["savefig.dpi"] = 600
plt.rcParams["interactive"] = True
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Arial"
plt.rcParams["mathtext.fontset"] = "custom"
plt.rcParams["mathtext.rm"] = "Arial"
plt.rcParams["mathtext.it"] = "Arial:italic"
plt.rcParams["mathtext.bf"] = "Arial:bold"



IMPORT_DIR = "../data/20210822"
RESULTS_DIR = "../results"

CODERS = ["remym", "lsowin", "rraider", "hcaldas", "hadaweh"] #"cmader", "kkonkoly"]
# random.shuffle(CODERS)

n_coders = len(CODERS)

with open("../code/labels.json", "r") as infile:
    themes = [ label["text"] for label in json.load(infile) ]
pos_color = "#4CAF50"
neg_color = "#F44336" 

posneg_breakpoint = themes.index("Sleep paralysis")
n_pos_themes = posneg_breakpoint
n_neg_themes = len(themes) - n_pos_themes
height_ratios = [ n_pos_themes, n_neg_themes ]


data = {}
for i, c in enumerate(CODERS):
    unique_coder_id = string.ascii_uppercase[i]
    # unique_coder_id = CODERS[i]
    import_fname = os.path.join(IMPORT_DIR, f"{c}.jsonl")
    with open(import_fname, "r") as infile:
        coder_data = [ json.loads(l) for l in infile.read().splitlines() ]
    # convert from list to a dict that has post id as keys and labels
    coder_data = { post["id"] : post["label"] for post in coder_data }
    data[unique_coder_id] = coder_data


row_list = []
for coder, coderdata in data.items():
    for postid, postlabels in coderdata.items():
        for start, end, subtheme in postlabels:
            payload = dict(coder=coder, postid=postid, subtheme=subtheme)
            row_list.append( payload )

df = pd.DataFrame(row_list)

# drop duplicates bc sometimes the same theme is there >1 in a single post
df = df.drop_duplicates().reset_index(drop=True)

expanded = df.groupby("subtheme")["postid"
    ].value_counts(dropna=False).unstack(fill_value=0
    ).reindex(themes, fill_value=0)


assert expanded.values.min() == 0
# assert expanded.values.max() == len(USERS)






######################################################################
## plot number of posts coded per coder
# sea.countplot(data=df, x="coder")
_, ax = plt.subplots(figsize=(2.5, 2.5), constrained_layout=True)
counts = df.groupby("coder").postid.nunique()
# xvals = range(counts.size)
yvals = counts.values
xticklabels = counts.index.tolist()
ax.bar(xticklabels, yvals, color="white", edgecolor="black", linewidth=1)
# ax.set_xticks(xvals)
# ax.set_xticklabels(xticklabels)
ax.set_ylabel("# of posts with coded content")
ax.set_xlabel("coder")
ax.set_ylim(0, 200)
ax.yaxis.set(major_locator=plt.MultipleLocator(50), minor_locator=plt.MultipleLocator(10))


export_fname = os.path.join(RESULTS_DIR, "coders.png")
plt.savefig(export_fname)
plt.close()


######################################################################
### binarize whether a post is or is not in a theme
### and plot simple counts
binarized = expanded >= 3 #(n_coders-1)
binarized_sum = binarized.sum(axis=1)

_, axes = plt.subplots(1, 2, figsize=(6.5, 2.5), constrained_layout=True,
    gridspec_kw=dict(width_ratios=height_ratios))
for ax in axes:
    if ax.is_first_col():
        subset = binarized_sum[:posneg_breakpoint]
        color = pos_color
    else:
        subset = binarized_sum[posneg_breakpoint:]
        color = neg_color
    xvals = range(subset.size)
    yvals = subset.values
    xticklabels = subset.index.tolist()
    ax.barh(xvals, yvals, color=color, edgecolor="black", linewidth=1)
    ax.set_yticks(xvals)
    ax.set_yticklabels(xticklabels, fontsize=8)#, rotation=33, ha="right")
    ax.set_xlabel("# of posts")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set(major_locator=plt.MultipleLocator(10), minor_locator=plt.MultipleLocator(1))
    ax.invert_yaxis()

for ax in axes:
    ax.set_xbound(upper=max([ max(ax.get_xlim()) for ax in axes ]))


export_fname = os.path.join(RESULTS_DIR, "subthemes.png")
plt.savefig(export_fname)
plt.close()


######################################################################
## draw a matrix with
## all unique posts going horizontal
## all unique themes going vertical
## each cell is a count of how many users coded it that way


# # get a list of all unique posts
# all_post_ids = []
# for user, udata in data.items():
#     for postid, postlabels in udata.items():
#         all_post_ids.append(postid)
# unique_post_ids = sorted( set(all_post_ids) )


# from matplotlib import colors
# colornorm = colors.Normalize(vmin=1, vmax=5)
masked_data = np.ma.masked_where(expanded.values == 0, expanded.values)


pos_data = masked_data[:posneg_breakpoint, :]
neg_data = masked_data[posneg_breakpoint:, :]

# args constant across plots
IMSHOW_ARGS = dict(vmin=0, vmax=n_coders, origin="upper",
    aspect="auto", interpolation="none")
fig, axes = plt.subplots(2, 2, figsize=(6,2.5),
    gridspec_kw=dict(height_ratios=height_ratios, width_ratios=[1,.02]),
    constrained_layout=True)

# ax1, ax2 = axes
ax1, cbar_ax1, ax2, cbar_ax2 = axes.flat

im1 = ax1.imshow(pos_data, cmap="Greens", **IMSHOW_ARGS)
im2 = ax2.imshow(neg_data, cmap="Reds", **IMSHOW_ARGS)

ax1.set_yticks(range(n_pos_themes))
ax2.set_yticks(range(n_neg_themes))
ax1.set_yticklabels(themes[:posneg_breakpoint], fontsize=8)
ax2.set_yticklabels(themes[posneg_breakpoint:], fontsize=8)

ax1.xaxis.set(major_locator=plt.NullLocator())
ax2.xaxis.set(major_locator=plt.NullLocator())

XLABEL = r"$\leftarrow$unique posts$\rightarrow$"
ax2.set_xlabel(XLABEL, fontsize=8)

# CBAR_MAJOR_TICKS = [0, n_coders]
# CBAR_MINOR_TICKS = range(n_coders)

# cbar1 = fig.colorbar(im1, cax=cbar_ax1, ticks=CBAR_MAJOR_TICKS, orientation="vertical")
cbar1 = fig.colorbar(im1, cax=cbar_ax1, orientation="vertical")
cbar2 = fig.colorbar(im2, cax=cbar_ax2, orientation="vertical")

cbar1.ax.tick_params(which="major", color="black", size=3, direction="in", labelsize=8)
cbar2.ax.tick_params(which="major", color="black", size=3, direction="in", labelsize=8)
cbar1.ax.tick_params(which="minor", color="black", size=2, direction="in")
cbar2.ax.tick_params(which="minor", color="black", size=2, direction="in")
cbar1.ax.yaxis.set(major_locator=plt.MultipleLocator(n_coders), minor_locator=plt.MultipleLocator(1))
cbar2.ax.yaxis.set(major_locator=plt.MultipleLocator(n_coders), minor_locator=plt.MultipleLocator(1))
# cbar1.ax.yaxis.set_ticks(CBAR_MINOR_TICKS, minor=True)
# cbar2.ax.yaxis.set_ticks(CBAR_MINOR_TICKS, minor=True)

CBAR_LABEL_ARGS = dict(labelpad=6, rotation=270, fontsize=8, va="center", ha="center")
cbar1.set_label("# of coders", **CBAR_LABEL_ARGS)
cbar2.set_label("# of coders", **CBAR_LABEL_ARGS)
# cbar.outline.set_visible(False)
# # cbar.outline.set_linewidth(.5)
# cbar.ax.set_ybound(lower=1)
# cbar.ax.yaxis.set_ticklabels([])

export_fname = os.path.join(RESULTS_DIR, "counts.png")
plt.savefig(export_fname)
plt.close()


######################################################################
### big plot showing coder consistency
###

big_df = df.groupby(["subtheme","coder"])["postid"].value_counts(dropna=False
    ).unstack(fill_value=0
    ).reindex(pd.MultiIndex.from_product([themes, data.keys()], names=["subtheme", "coder"]),
        axis="index", fill_value=0
    ).T


fig, axes = plt.subplots(1, len(themes), figsize=(6.5, 3),
    constrained_layout=True)

for ax, subtheme in zip(axes, themes):
    plot_df = big_df[subtheme]
    plot_data = plot_df.values
    masked_data = np.ma.masked_where(plot_data == 0, plot_data)
    if themes.index(subtheme) < posneg_breakpoint:
        cmap = "Greens"
    else:
        cmap = "Reds"
    im = ax.imshow(masked_data, cmap=cmap,
        vmin=0, vmax=1,
        origin="upper", aspect="auto", interpolation="none")
    ax.set_yticks([])
    ax.set_title(subtheme.replace(" ", "\n"), fontsize=8, rotation=90, ha="center", va="bottom")
    if ax.is_first_col():
        ax.xaxis.tick_top()
        ax.set_xticks(range(n_coders))
        ax.set_xticklabels(plot_df.columns.tolist(), fontsize=8)
        LABEL = r"$\leftarrow$unique posts$\rightarrow$"
        ax.set_ylabel(LABEL, fontsize=8)
    else:
        # ax.axis("off")
        ax.set_xticks([])
        # plt.tick_params(axis='both', which='both', bottom='off', top='off', labelbottom='off', right='off', left='off', labelleft='off')
    # ax.yaxis.set(minor_locator=plt.MultipleLocator(1))
    ax.hlines(np.linspace(*ax.get_ylim()[::-1], len(plot_df)+1),
        ax.get_xbound()[0], ax.get_xbound()[1],
        linewidth=.2, alpha=.5, color="gainsboro")
    # ax.vlines(line_locs, ymins, ymaxs, **LINE_ARGS)

export_fname = os.path.join(RESULTS_DIR, "everything.png")
plt.savefig(export_fname)
plt.close()



######################################################################
## plot subtheme overlap
overlap = lambda a, b: np.column_stack([a,b]).all(axis=1).sum()

# note that corr returns 1 for diagonal by default
# (even though we r kinda hijacking it here)
img = binarized.T.corr(overlap).reindex(themes).values


upper_indx = np.triu_indices_from(img, k=0)
img[upper_indx] = 0
masked_img = np.ma.masked_where(img==0, img)

fig, ax = plt.subplots(figsize=(5,5), constrained_layout=True)
im = ax.imshow(img, cmap="binary", interpolation="none")

# ax.yaxis.set(major_locator=plt.MultipleLocator(1))
ax.set_yticks(range(len(themes)))
ax.set_yticklabels(themes, fontsize=8)
ax.set_xticks(range(len(themes)))
ax.set_xticklabels(themes, fontsize=8, rotation=30, ha="right")
# ax.yaxis.set(minor_locator=plt.MultipleLocator(4))
# ax.grid(True, which="minor")

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

n_subthemes = len(themes)

line_locs = np.linspace(*ax.get_ylim()[::-1], n_subthemes+1)[:-1]
line_mins_h = np.repeat(ax.get_xbound()[0], n_subthemes)
line_mins_v = np.repeat(ax.get_xbound()[1], n_subthemes)
line_maxs = np.linspace(ax.get_xbound()[0], ax.get_xbound()[1]-1, n_subthemes)
LINE_ARGS = dict(linewidth=.5, alpha=1, color="gainsboro")
ax.hlines(line_locs, line_mins_h, line_maxs, **LINE_ARGS)
ax.vlines(line_locs, line_mins_v, line_maxs, **LINE_ARGS)

rect_pos = plt.matplotlib.patches.Rectangle(
    (ax.get_xlim()[0], ax.get_ylim()[0]-n_neg_themes),
    n_pos_themes, -n_pos_themes, linewidth=1, edgecolor="g", facecolor="none", clip_on=False)
rect_neg = plt.matplotlib.patches.Rectangle(
    (ax.get_xlim()[0]+n_pos_themes, ax.get_ylim()[0]),
    n_neg_themes, -n_neg_themes, linewidth=1, edgecolor="r", facecolor="none", clip_on=False)

ax.add_patch(rect_pos)
ax.add_patch(rect_neg)

cbar_ax = fig.add_axes([.7, .8, .2, .02])
cbar = fig.colorbar(im, cax=cbar_ax, orientation="horizontal")
cbar.ax.tick_params(which="major", color="black", size=3, direction="out", labelsize=8)
cbar.ax.tick_params(which="minor", color="black", size=2, direction="out")
cbar.ax.xaxis.set(major_locator=plt.MultipleLocator(5), minor_locator=plt.MultipleLocator(1))
CBAR_LABEL_ARGS = dict(labelpad=6, rotation=270, fontsize=8, va="center", ha="center")
cbar.set_label("# of posts with overlap", fontsize=8, labelpad=6)
# cbar.outline.set_visible(False)
# # cbar.outline.set_linewidth(.5)
# cbar.ax.set_ybound(lower=1)
# cbar.ax.yaxis.set_ticklabels([])
# cbar.set_label("# of users", x=1.1, fontsize=8, labelpad=-14, va="center", ha="left")
# # cbar.ax.set_title("title_test")
# # cbar.set_ticks([1,10,100,1000])
# cax.tick_params(labelsize=8, length=2)
# cbar.locator = plt.LogLocator(base=10)
# cbar.formatter = plt.ScalarFormatter()
# cbar.update_ticks()

export_fname = os.path.join(RESULTS_DIR, "overlap.png")
plt.savefig(export_fname)
plt.close()



# ######################################################################

# # plot timecourse of lucidity without control posts

# for post_id, row in binarized.T.iterrows():
#     if row["Lucidity without control"]:
#         if row["Dream enhancement"]:

#             print("f")
#         if row["Lucid nightmares"]:
#             print("fe")

# labeler1 = [2, 0, 2, 2, 0, 1]
# labeler2 = [0, 0, 2, 2, 0, 2]
# cohen_kappa_score(labeler1, labeler2)

kappa_scores = {}
alpha_scores = {}
icc_scores = {}

for col in themes:

    #### !!!! these probably aren't accounting for posts that noone identified as anything
    ##### but I guess that's okay.

    # extract the scores for only this subtheme
    stheme_ratings = big_df[col]

    vals = stheme_ratings.values
    table, bins = inter_rater.aggregate_raters(vals, n_cat=2)
    fk = inter_rater.fleiss_kappa(table, method="fleiss")
    
    vals = stheme_ratings.values[:,:2]
    table, bins = inter_rater.to_table(vals, bins=2)
    ca = inter_rater.cohens_kappa(table, return_results=False)

    # icc across all coders
    a = stheme_ratings.reset_index().melt(id_vars="postid")
    icc = pg.intraclass_corr(data=a, targets="postid", raters="coder", ratings="value")
    icc_scores[col] = icc.iloc[0,2]

    # Scott's pi

    # Krippendorff's alpha
    # krippindorff across all coders (and all subthemes too??)
    reliability_data = [ list(x.flatten()) for x in np.hsplit(stheme_ratings.values, n_coders) ]
    alpha = krippendorff.alpha(reliability_data=reliability_data,
        level_of_measurement="nominal")
    alpha_scores[col] = alpha

    # Cohen's kappa
    # kappa statistic can only be done on 2 coders at a time,
    # so do this iteratively for all coder combos
    # and basic percent agreement?
    kappa_list = []
    pct_list = []
    for c1, c2 in itertools.combinations(stheme_ratings.columns, 2):
        r1, r2 = stheme_ratings[[c1,c2]].T.values
        k = cohen_kappa_score(r1, r2)
        pct = np.mean(r1 == r2)
        kappa_list.append(dict(coder1=c1, coder2=c2, kappa=k, pct=pct))
    kappa_scores[col] = kappa_list


# build kappa dataframe
ka = pd.concat([ pd.DataFrame(scores,
    index=np.repeat(st,len(scores))) for st, scores in kappa_scores.items() ]
).rename_axis("subtheme")

# build alpha dataframe
alpha_df = pd.DataFrame.from_dict(alpha_scores, orient="index"
    ).rename_axis("subtheme").rename(columns={0:"alpha"})
# build icc dataframe
icc_df = pd.DataFrame.from_dict(icc_scores, orient="index"
    ).rename_axis("subtheme").rename(columns={0:"icc"})

# merge alpha and icc
irr_df = alpha_df.join(icc_df)


########################################################
# plot kappa

n_themes = len(themes)
# n_axes_1side = np.ceil(np.sqrt(n_themes)).astype(int)

fig, axes = plt.subplots(2, 7, figsize=(6.5,2.5), constrained_layout=True)

for i, st in enumerate(themes):
    if i < posneg_breakpoint:
        ax = axes[0, i]
    else:
        ax = axes[1, i-posneg_breakpoint]
    plot_img = ka.loc[st].pivot("coder2", "coder1", "kappa").reindex(index=stheme_ratings.columns, columns=stheme_ratings.columns)
    im = ax.imshow(plot_img, vmin=-1, vmax=1, cmap="PuOr")
    ax.set_title(st.replace(" ", "\n", 1), fontsize=8)
    if ax.is_first_col() and ax.is_first_row():
        ax.set_xticks(range(stheme_ratings.columns.size))
        ax.set_yticks(range(stheme_ratings.columns.size))
        # ax.set_xticklabels(stheme_ratings.columns, fontsize=8, rotation=33, ha="right")
        ax.set_xticklabels([ st[:2] for st in stheme_ratings.columns ], fontsize=8)
        ax.set_yticklabels(stheme_ratings.columns, fontsize=8)
        ax.set_ylabel("coder", fontsize=8)
    else:
        ax.xaxis.set(major_locator=plt.NullLocator())
        ax.yaxis.set(major_locator=plt.NullLocator())

    line_locs = np.linspace(*ax.get_ylim()[::-1], n_coders+1)[:-1]
    line_mins_h = np.repeat(ax.get_xbound()[0], n_coders)
    line_mins_v = np.repeat(ax.get_xbound()[1], n_coders)
    line_maxs = np.linspace(ax.get_xbound()[0], ax.get_xbound()[1]-1, n_coders)
    LINE_ARGS = dict(linewidth=.5, alpha=1, color="black")
    ax.hlines(line_locs, line_mins_h, line_maxs, **LINE_ARGS)
    ax.vlines(line_locs, line_mins_v, line_maxs, **LINE_ARGS)

# plt.colorbar(im, cax=axes[0, -1])
axes[0, -1].axis("off")
cbar_ax = fig.add_axes([.92, .55, .02, .3])
cbar = fig.colorbar(im, cax=cbar_ax, orientation="vertical")
cbar.ax.tick_params(which="major", color="black", size=3, direction="out", labelsize=8)
cbar.ax.tick_params(which="minor", color="black", size=2, direction="out")
cbar.ax.yaxis.set(major_locator=plt.MultipleLocator(1), minor_locator=plt.MultipleLocator(.5))
# CBAR_LABEL_ARGS = dict(labelpad=6, rotation=270, fontsize=8, va="center", ha="center")
cbar.set_label("Cohen's kappa", fontsize=8, labelpad=6)
cbar.ax.yaxis.set_label_position("left")

# fig.suptitle("Inter-rater reliability")
export_fname = os.path.join(RESULTS_DIR, "irr_kappa.png")
plt.savefig(export_fname)
plt.close()


############################ repeat for pct agreement

############################ pct agreement at different cutoffs? (1 coder, 2 coders, 3, 4, 5)
########################### or is this just the earlier plot? (it's possible for both)




########################################################
# plot alpha and icc together

def my_formatter(x, pos):
    val_str = '{:g}'.format(x)
    return val_str.replace("0", "", 1) if np.abs(x) > 0 and np.abs(x) < 1 else val_str


fig, axes = plt.subplots(2, figsize=(3,4), constrained_layout=True,
    gridspec_kw={"height_ratios":height_ratios},
    sharex=True, sharey=False)

BAR_ARGS = dict(edgecolor="k", linewidth=1, height=.8)

for ax in axes:
    if ax.is_first_row():
        x = irr_df[:posneg_breakpoint].index.tolist()
        y1 = irr_df[:posneg_breakpoint]["alpha"].tolist()
        color = pos_color
    else:
        x = irr_df[posneg_breakpoint:].index.tolist()
        y1 = irr_df[posneg_breakpoint:]["alpha"].tolist()
        color = neg_color
    ax.barh(x, y1, color=color, **BAR_ARGS)

    ax.axvline(0, color="k", lw=1, linestyle="-")
    ax.axvline(.8, color="gold", lw=1, linestyle="--")

    ax.set_xbound(lower=-.1, upper=1)
    ax.xaxis.set(major_formatter=plt.FuncFormatter(my_formatter),
        major_locator=plt.MultipleLocator(.5), minor_locator=plt.MultipleLocator(.1))
    ax.invert_yaxis()
    ax.tick_params(axis="both", which="major", labelsize=8)

ax.set_xlabel("Krippendorff's alpha", fontsize=8)


export_fname = os.path.join(RESULTS_DIR, "irr_alpha.png")
plt.savefig(export_fname)
plt.close()






