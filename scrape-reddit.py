"""Scrape all of r/LucidDreaming.
"""
import os
import tqdm
import datetime
import pandas as pd
from psaw import PushshiftAPI
import utils

SUBREDDIT = "LucidDreaming"

SUBMISSION_FILTERS = [
    "created_utc",
    "subreddit",
    "subreddit_id",
    "id",
    "author",
    "author_fullname",
    "link_flair_text",
    "num_comments",
    "total_awards_received",
    "score",
    "upvote_ratio",
    "is_video",
    "title",
    "selftext",
]

# Generate a timestamped filename for exporting.
now_string = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S")
export_basename = f"r-{SUBREDDIT}_{now_string}.csv"
export_fullpath = os.path.join(utils.Config.data_directory, "source", export_basename)
export_fullpath_pickle = export_fullpath.replace(".csv", ".pkl")

# Find all relevant Reddit posts.
api = PushshiftAPI()
gen = api.search_submissions(subreddit=SUBREDDIT, filter=SUBMISSION_FILTERS)

# Grab all the posts and turn into a dataframe (takes a while).
df = pd.DataFrame([ thing.d_ for thing in tqdm.tqdm(gen, desc="scraping") ])

# Reorder columns, including the "created" stamp.
column_order = ["created"] + SUBMISSION_FILTERS
df = df[column_order]

# Export as a csv file.
df.to_csv(export_fullpath, encoding="utf-8-sig", index=False, na_rep="NA")

# Export as a pickle file as backup.
df.to_pickle(export_fullpath_pickle)
