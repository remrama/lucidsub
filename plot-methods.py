"""Draw a 2-panel figure.
Panel 1: All-time r/LucidDreaming post frequency (over time).
Panel 2: Box&Arrow diagram for content analysis procedure.
"""
import os
import pandas as pd

import seaborn as sea
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches

import utils
utils.load_matplotlib_settings()


# I/O
basename = f"r-LucidDreaming_{utils.Config.scrape_timestamp}.csv"
import_fname = os.path.join(utils.Config.data_directory, "source", basename)
export_fname = os.path.join(utils.Config.data_directory, "results", "methods.png")
export_fname_txt = os.path.join(utils.Config.data_directory, "results", "post_frequency.txt")


############################## Load and manipulate data.

df = pd.read_csv(import_fname, encoding="utf-8", low_memory=False)

# Sort by timestamp.
df["timestamp"] = pd.to_datetime(df["created_utc"], unit="s", utc=True)
df = df.sort_values("timestamp", ascending=True).reset_index(drop=True)

# Remove deleted posts, removed posts, and posts without any text.
df = df[ ~df["selftext"].isin(["[deleted]", "[removed]"]) ]
df = df.dropna(subset=["selftext"])


############################## Save out mean post frequency to a text file.

monthly_mean = df.groupby(pd.Grouper(freq="M", key="timestamp")
    ).size().loc["2015":"2019"].mean()
mean_txt = f"Monthly mean from 2015 to 2019 is {monthly_mean:.1f}"
with open(export_fname_txt, "wt", encoding="utf-8") as f:
    f.write(mean_txt)


############################## Define plot parameters and open general figure.

FIGSIZE = (7.5, 3)

# Open figure for both panels.
fig, (ax, ax2) = plt.subplots(ncols=2, figsize=FIGSIZE,
    gridspec_kw=dict(left=.1, right=1, bottom=.15, top=.95,
                     wspace=.1, width_ratios=[2.3, 1]))

# Draw the A and B letters, for first and second panels.
fig.text(0, 1, "A", fontsize=12, fontweight="bold", ha="left", va="top")
fig.text(.73, 1, "B", fontsize=12, fontweight="bold", ha="left", va="top")



############################## Draw first panel (Reddit post timecourse).

YMAX = 4000
YTICK_MINOR = 100
YTICK_MAJOR = 1000
GRID_COLOR = "gainsboro"
GRID_LINEWIDTH = dict(major=1, minor=.3)

# Generate monthly bins.
XMIN = pd.to_datetime("2009-06-01")
XMAX = pd.to_datetime("2021-06-01")
n_years = (XMAX-XMIN).days // 365
n_bins = n_years * 12 # to get 1 bin/tick per month
binrange = (mdates.date2num(XMIN), mdates.date2num(XMAX))

# Draw histogram.
sea.histplot(data=df, x="timestamp",
    bins=n_bins, binrange=binrange,
    stat="count", cumulative=False,
    element="bars", fill=True,
    color="gainsboro", alpha=1,
    linewidth=.5, edgecolor="black",
    ax=ax)

# a e s t h e t i c s
ax.set_xlabel("Date (year)")
ax.set_ylabel("Post frequency (monthly)")
ax.set_ybound(upper=YMAX)
ax.set_xlim(XMIN, XMAX)
ax.tick_params(which="both", axis="y", direction="in")
for which in ["major", "minor"]:
    ax.tick_params(which=which, axis="y", grid_color=GRID_COLOR,
                   grid_linewidth=GRID_LINEWIDTH[which])
ax.grid(which="both", axis="y")
ax.yaxis.set(major_locator=plt.MultipleLocator(YTICK_MAJOR),
             minor_locator=plt.MultipleLocator(YTICK_MINOR))
ax.xaxis.set(major_locator=mdates.YearLocator(),
             minor_locator=mdates.MonthLocator(),
             major_formatter=mdates.DateFormatter("%Y"))
ax.set_axisbelow(True)




############################## Draw second panel (content analysis box&arrow).

FONT_SIZE = 10
LEFTEST = .05 # starting left point for boxes
HIGHEST = .98 # starting top point for boxes
BOX_WIDTH = .75
BOX_HEIGHT = .25
BOX_VGAP = .1 # vertical gap between bozes
LEFT_TXT_BUFFER = .01 # how far off the inner box edge to start text
BOX_STYLE = "round, pad=0"
ARROW_STYLE = "Simple, tail_width=0.5, head_width=4, head_length=8"
STEP4_TEXT = "Repeat as needed"
TEXTS = [
    ("Develop themes\n"
    + "from prior research\n"
    + "and r/LucidDreaming"),

    ("Raters code subset\n"
    + "of posts for old and\n"
    + "new themes"),

    ("Meet, discuss, and\n"
    + "adjust themes based\n"
    + "on new insights"),
]

xpositions = [LEFTEST] * 3
ypositions = [ HIGHEST - (i+1)*BOX_HEIGHT - i*BOX_VGAP for i in range(3) ]
arrow_kw = dict(arrowstyle=ARROW_STYLE, color="k", lw=1)
transform = ax2.transAxes

ax2.set_xlim(0, 1)
ax2.set_ylim(0, 1)
ax2.axis("off")


# Draw the three text boxes, one per loop.

for txt, x, y in zip(TEXTS, xpositions, ypositions):

    # Draw the box.
    bottomleft_xy = (x, y)
    rect = mpatches.FancyBboxPatch(bottomleft_xy,
        BOX_WIDTH, BOX_HEIGHT, facecolor="white",
        boxstyle=BOX_STYLE, transform=transform)
    ax2.add_patch(rect)

    # Draw the text.
    text_x = x + LEFT_TXT_BUFFER
    text_y = y + BOX_HEIGHT/2
    ax2.text(text_x, text_y, txt, transform=transform,
        fontsize=FONT_SIZE, ha="left", va="center")

    # Draw the arrow.
    if txt.startswith("Meet"):
        # curved arrow going back up
        arrow_xy1 = (x+BOX_WIDTH, y+BOX_HEIGHT/2) # middle right of this box
        arrow_xy2 = (x+BOX_WIDTH, y+BOX_HEIGHT*1.5+BOX_VGAP) # middle right of next box
        arrow = mpatches.FancyArrowPatch(arrow_xy1, arrow_xy2,
            connectionstyle="arc3,rad=.5", **arrow_kw)
    else:
        arrow_xy1 = (x+BOX_WIDTH/2, y) # bottom of this box
        arrow_xy2 = (x+BOX_WIDTH/2, y-BOX_VGAP) # top of next box
        arrow = mpatches.FancyArrowPatch(arrow_xy1, arrow_xy2, **arrow_kw)
    ax2.add_patch(arrow)

    # Add extra text for step 4.
    if txt.startswith("Meet"):
        vert_x = x + BOX_WIDTH + .13 # some guessing to get past the curved arrow bump
        vert_y = y + BOX_HEIGHT + BOX_VGAP/2
        ax2.text(vert_x, vert_y, STEP4_TEXT,
            transform=transform, rotation=270,
            fontsize=FONT_SIZE, ha="left", va="center")



# Export!
plt.savefig(export_fname)
utils.save_hires_copies(export_fname)
plt.close()