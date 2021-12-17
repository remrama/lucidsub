"""
show general r/LucidDreaming post frequency

and panel for content analysis methods
"""
import os
import pandas as pd
import config as c

import seaborn as sea
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
plt.rcParams["savefig.dpi"] = 600
plt.rcParams["interactive"] = True
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Arial"


import_fname = os.path.join(c.DATA_DIR, "r-LucidDreaming_20210607T232348.csv")
export_fname = os.path.join(c.RESULTS_DIR, "plots", "reddit-postfrequency.png")

### load and manipulate data a bit

df = pd.read_csv(import_fname, encoding="utf-8", low_memory=False)

df["timestamp"] = pd.to_datetime(df["created_utc"], unit="s", utc=True)
df = df.sort_values("timestamp", ascending=True).reset_index(drop=True)

# remove deleted posts, removed posts, and posts without any text
df = df[ ~df["selftext"].isin(["[deleted]", "[removed]"]) ]
df = df.dropna(subset=["selftext"])


YMAX = 4000
YTICK_MAJOR = 1000
YTICK_MINOR = 100
GRID_COLOR = "gainsboro"
GRID_LINEWIDTH = dict(major=1, minor=.3)

# generate monthly bins
XMIN = pd.to_datetime("2009-06-01")
XMAX = pd.to_datetime("2021-06-01")
n_years = (XMAX-XMIN).days // 365
n_bins = n_years * 12 # to get 1 bin/tick per month
binrange = (mdates.date2num(XMIN), mdates.date2num(XMAX))


FIGSIZE = (7.5, 3)
fig, (ax, ax2) = plt.subplots(ncols=2, figsize=FIGSIZE,
    gridspec_kw=dict(left=.1, right=1, bottom=.15, top=.95,
        wspace=.1, width_ratios=[2.5, 1]))
fig.text(0, 1, "A", fontsize=12, fontweight="bold", ha="left", va="top")
fig.text(.75, 1, "B", fontsize=12, fontweight="bold", ha="left", va="top")



sea.histplot(data=df, x="timestamp",
    bins=n_bins, binrange=binrange,
    stat="count", cumulative=False,
    element="bars", fill=True,
    color="gainsboro", alpha=1,
    linewidth=.5, edgecolor="black",
    ax=ax)

###### aesthetics
ax.set_xlabel("date (year)")
ax.set_ylabel("Number of posts (monthly)")
ax.set_ybound(upper=YMAX)
ax.set_xlim(XMIN, XMAX)
# ax.spines["top"].set_visible(False)
# ax.spines["right"].set_visible(False)
ax.tick_params(which="both", axis="y", direction="in")
for which in ["major", "minor"]:
    ax.tick_params(which=which, axis="y",
        grid_color=GRID_COLOR, grid_linewidth=GRID_LINEWIDTH[which])
ax.grid(which="both", axis="y")
ax.yaxis.set(major_locator=plt.MultipleLocator(YTICK_MAJOR),
             minor_locator=plt.MultipleLocator(YTICK_MINOR))
ax.xaxis.set(major_locator=mdates.YearLocator(),
             minor_locator=mdates.MonthLocator(),
             major_formatter=mdates.DateFormatter("%Y"))
ax.set_axisbelow(True)


# ######## draw shading at periods of data collection

# COLLECTION_DATES = ["2019-04-01", "2019-07-01"]
# COLLECTION_TEXT = ["200 April posts", "200 July posts"]

# LINE_ARGS = dict(color="k", lw=1, ls="dashed", zorder=0)
# TEXT_ARGS = dict(ha="left", va="top", fontsize=10)

# for i, date_str in enumerate(COLLECTION_DATES):
#     xval = pd.to_datetime(date_str)
#     ax.axvline(xval, **LINE_ARGS)
#     yval = .95 - i*.07
#     txt = " " + COLLECTION_TEXT[i]
#     ax.text(xval, yval, txt, transform=ax.get_xaxis_transform(), **TEXT_ARGS)


############################# PANEL B -- content analysis box/arrows methods diagram

# draw 3 boxes in a row
leftest = .05
highest = .98
boxwidth = .75
boxheight = .25
boxgap = .1
texts = [
    ("Develop themes\n"
    + "from prior research\n"
    + "and r/LucidDreaming"),

    ("Raters code subset\n"
    + "of posts for old\n"
    + "and new themes"),

    ("Meet, discuss\n"
    + "and adjust based\n"
    + "on new insights"),
]
xpositions = [leftest] * 3
ypositions = [ highest - (i+1)*boxheight - i*boxgap for i in range(3) ]
boxstyle = "round, pad=0"
transform = ax2.transAxes

arrowstyle = "Simple, tail_width=0.5, head_width=4, head_length=8"
arrow_kw = dict(arrowstyle=arrowstyle, color="k", lw=1)

ax2.set_xlim(0, 1)
ax2.set_ylim(0, 1)
ax2.axis("off")
left_txtbuff = .01

for txt, x, y in zip(texts, xpositions, ypositions):

    # easiest solution is to draw text and box at ONCE with a textbox
    # but it's tough to set the width of the box (it fits to text)
    # textbox_props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
    # t = ax.text(x, y, txt, transform=ax.transAxes,
    #     fontsize=10, va="bottom", ha="left",
    #     bbox=textbox_props)
    # bb = t.get_bbox_patch()

    # draw box
    bottomleft_xy = (x, y) # lower left corner of box
    rect = mpatches.FancyBboxPatch(
        bottomleft_xy,
        boxwidth, boxheight, facecolor="white",
        boxstyle=boxstyle, transform=transform)
    ax2.add_patch(rect)

    # draw text
    text_x = x+left_txtbuff
    text_y = y+boxheight/2
    ax2.text(text_x, text_y, txt,
        transform=transform,
        fontsize=10, ha="left", va="center")


    # draw arrow
    if txt.startswith("Meet"):
        # curved arrow going back up
        arrow_xy1 = (x+boxwidth, y+boxheight/2) # middle right of this box
        arrow_xy2 = (x+boxwidth, y+boxheight*1.5+boxgap) # middle right of next box
        arrow = mpatches.FancyArrowPatch(
            arrow_xy1, arrow_xy2,
            connectionstyle="arc3,rad=.5", **arrow_kw)
    else:
        arrow_xy1 = (x+boxwidth/2, y) # bottom of this box
        arrow_xy2 = (x+boxwidth/2, y-boxgap) # top of next box
        arrow = mpatches.FancyArrowPatch(
            arrow_xy1, arrow_xy2, **arrow_kw)
    ax2.add_patch(arrow)

    # add extra text for step 4
    if txt.startswith("Meet"):
        step4txt = "Repeat as needed"
        vert_x = x+boxwidth+.1 # some guessing to get past the curved arrow bump
        vert_y = y+boxheight+boxgap/2
        ax2.text(vert_x, vert_y, step4txt,
            transform=transform,
            rotation=270,
            fontsize=10, ha="left", va="center")




plt.savefig(export_fname)
plt.close()