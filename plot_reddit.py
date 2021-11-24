"""
show general r/LucidDreaming post frequency
"""
import os
import pandas as pd
import config as c

import seaborn as sea
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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


_, ax = plt.subplots(figsize=(6, 3), constrained_layout=True)

sea.histplot(data=df, x="timestamp",
    bins=n_bins, binrange=binrange,
    stat="count", cumulative=False,
    element="bars", fill=True,
    color="gainsboro", alpha=1,
    linewidth=.5, edgecolor="black")

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


######## draw shading at periods of data collection

COLLECTION_DATES = ["2019-04-01", "2019-07-01"]
COLLECTION_TEXT = ["200 April posts", "200 July posts"]

LINE_ARGS = dict(color="k", lw=1, ls="dashed", zorder=0)
TEXT_ARGS = dict(ha="left", va="top", fontsize=10)

for i, date_str in enumerate(COLLECTION_DATES):
    xval = pd.to_datetime(date_str)
    ax.axvline(xval, **LINE_ARGS)
    yval = .95 - i*.07
    txt = " " + COLLECTION_TEXT[i]
    ax.text(xval, yval, txt, transform=ax.get_xaxis_transform(), **TEXT_ARGS)



plt.savefig(export_fname)
plt.close()