"""Process the initial Reddit scrape, prior to manual/content coding.
Very minimal cleaning and extraction of a small subset of posts.

Take the first 200 posts from any month, but always from 2019.
"""
import os
import time
import json
import argparse
import pandas as pd
import utils

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--month", type=str, required=True, help="Pick a month to take posts from (in 2019).")
args = parser.parse_args()


MONTH_STR = args.month
FIRST_N = 200 # save out the first N posts
YEAR = 2019 # take from the request month, in this year
KEEP_COLUMNS = ["id", "timestamp", "author", "title", "selftext"] # keep this subset for clean datafile


# I/O
import_basename = f"r-LucidDreaming_{utils.Config.scrape_timestamp}.csv"
import_fullpath = os.path.join(utils.Config.data_directory, "source", import_basename)
export_basename = f"r-LucidDreaming_2019{MONTH_STR.capitalize()}+200.csv"
export_fullpath = os.path.join(utils.Config.data_directory, "derivatives", export_basename)
export_fullpath_jsonl = export_fullpath.replace(".csv", ".jsonl")

# Load full originally scraped Reddit data.
df = pd.read_csv(import_fullpath, encoding="utf-8", low_memory=False)

# Remove deleted posts, removed posts, and posts without any text.
df = df[ ~df["selftext"].isin(["[deleted]", "[removed]"]) ]
df = df.dropna(subset=["selftext"])

# Sort by old to new.
df = df.sort_values("created_utc", ascending=True).reset_index(drop=True)
df["timestamp"] = pd.to_datetime(df["created_utc"], unit="s", utc=True)

# Extract a subset of posts, based on date.
month_digit = time.strptime(MONTH_STR, "%B").tm_mon # get month's digit
df = df[ df["timestamp"] >= f"{YEAR}-{month_digit:02d}-01" ][:FIRST_N]

# Extract a subset of columns.
# take subset of columns (others can be regained later)
df = df[KEEP_COLUMNS]



# Export as a csv.
df.to_csv(export_fullpath, index=False, encoding="utf-8",
    na_rep="NA", date_format="%Y-%m-%d %H:%M:%S")

# Export as a jsonl file, for Doccano.
with open(export_fullpath_jsonl, "w", encoding="utf-8") as outfile:

    # loop over each row and export with a line between title and text
    for _, row in df.iterrows():
        post_id = row["id"]
        title = row["title"]
        report = row["selftext"]
        title_and_report = "\n::-------------::\n\n".join([title, report])
        data = {
            "text" : title_and_report,
            "id" : post_id,
            "label" : [], # include for doccano
        }
        json.dump(data, outfile, ensure_ascii=False)
        outfile.write("\n")
