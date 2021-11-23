"""very minimal cleaning of the initial r/Dreams scrape,
prior to manual coding.

And get a few months for first pass at manual coding.
"""
import os
import argparse
import pandas as pd

import config as c



parser = argparse.ArgumentParser()
parser.add_argument("-m", "--month", type=str, required=True)
args = parser.parse_args()


# this is clunky and stupid but just cleaning up and not gonna mess with it
MONTH_STR = args.month
if MONTH_STR == "April":
    MONTH_DIG = "04"
elif MONTH_STR == "July":
    MONTH_DIG = "07"
else:
    raise ValueError("unexpected month argument")
    

import_fname = os.path.join(c.DATA_DIR, "r-LucidDreaming_20210607T232348.csv")
export_fname = os.path.join(c.DATA_DIR, f"r-LucidDreaming_2019{MONTH_STR}+200.csv")

# unix2dt = lambda ts: datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

df = pd.read_csv(import_fname,
    encoding="utf-8", low_memory=False)

# remove deleted posts, removed posts, and posts without any text
df = df[ ~df["selftext"].isin(["[deleted]", "[removed]"]) ]
df = df.dropna(subset=["selftext"])


# sort by old to new posts
df = df.sort_values("created_utc", ascending=True
    ).reset_index(drop=True)

df["timestamp"] = pd.to_datetime(df["created_utc"], unit="s", utc=True)
    # ).dt.strftime("%Y-%m-%d %H:%M:%S")
# extract certain dates
# df = df[ df["timestamp"].between("2020-02", "2020-05") ]
df = df[ df["timestamp"] >= f"2019-{MONTH_DIG}-01" ][:200]

# take subset of columns (others can be regained later)
df = df[ ["id", "timestamp", "author", "title", "selftext"] ]

# export
df.to_csv(export_fname, index=False, encoding="utf-8",
    na_rep="NA", date_format="%Y-%m-%d %H:%M:%S")
