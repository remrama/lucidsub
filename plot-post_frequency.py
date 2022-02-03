"""Visualize all-time r/LucidDreaming post frequency,
with a monthly timecourse.
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
export_fname = os.path.join(utils.Config.data_directory, "results", "post-frequency.png")
export_fname_txt = os.path.join(utils.Config.data_directory, "results", "post-frequency.txt")


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


############################## Plot it.

FIGSIZE = (5.5, 1.5)

# Open figure.
fig, ax= plt.subplots(figsize=FIGSIZE, constrained_layout=True)

# Pick parameters.
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


# Export!
plt.savefig(export_fname)
utils.save_hires_copies(export_fname)
plt.close()