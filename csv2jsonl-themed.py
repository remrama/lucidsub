"""
generate a jsonl file of all the posts
that were "themed" with something.
to upload to doccano for control ratings
"""
import os
import json
import pandas as pd

import config as c


import_fname = os.path.join(c.RESULTS_DIR, "themes-highlights_table.csv")
export_fname = os.path.join(c.RESULTS_DIR, "themed_posts.jsonl")

# load data
df = pd.read_csv(import_fname)
ser = df[["post_id", "full_txt"]].drop_duplicates(
    ).set_index("post_id").squeeze()

# mix them up
ser = ser.sample(frac=1, random_state=1)

# open a file that will continuously be written into
with open(export_fname, "w", encoding="utf-8") as outfile:

    # loop over each row and export with a line between title and text
    for post_id, txt in ser.items():
        payload = {
            "text" : txt,
            "id" : post_id,
            "label" : [], # include for doccano
        }
        json.dump(payload, outfile, ensure_ascii=False)
        outfile.write("\n")
