"""scrape all of r/Dreams
"""
import os
import tqdm
import datetime

import pandas as pd

from psaw import PushshiftAPI

import config as c

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

now_string = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S")

export_fname = os.path.join(c.DATA_DIR, f"r-{SUBREDDIT}_{now_string}.csv")

api = PushshiftAPI()
gen = api.search_submissions(subreddit=SUBREDDIT, filter=SUBMISSION_FILTERS)

# this step takes a while, gen is a generator and gets unpacked here
df = pd.DataFrame([ thing.d_ for thing in tqdm.tqdm(gen, desc="scraping") ])

# reorder columns in the order of submission filter list (add the automatically added "created")
column_order = ["created"] + SUBMISSION_FILTERS
df = df[column_order]

# # sort by old to new posts
# df = df.sort_values("created_utc", ascending=True).reset_index(drop=True)

# export as tsv
df.to_csv(export_fname, encoding="utf-8-sig", index=False, na_rep="NA")

# export as pickle in case dataframe fucks up or something
pickle_fname = export_fname.replace(".csv", ".pkl")
df.to_pickle(pickle_fname)

