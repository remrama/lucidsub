"""Load in cleaned up r/LucidDreaming data
and export as jsonl file for Doccano import.
"""
import os
import json
import argparse
import pandas as pd

import config as c


parser = argparse.ArgumentParser()
parser.add_argument("-m", "--month", type=str, required=True)
args = parser.parse_args()


MONTH_STR = args.month


import_fname = os.path.join(c.DATA_DIR, f"r-LucidDreaming_2019{MONTH_STR}+200.csv")
export_fname = os.path.join(c.DATA_DIR, f"r-LucidDreaming_2019{MONTH_STR}+200.jsonl")

# load data
df = pd.read_csv(import_fname, encoding="utf-8")

# open a file that will continuously be written into
with open(export_fname, "w", encoding="utf-8") as outfile:

    # loop over each row and export with a line between title and text
    for _, row in df.iterrows():
        post_id = row["id"]
        title = row["title"]
        report = row["selftext"]
        title_and_report = "\n::-------------::\n\n".join([title, report])
        payload = {
            "text" : title_and_report,
            "id" : post_id,
            "label" : [], # include for doccano
        }
        json.dump(payload, outfile, ensure_ascii=False)
        outfile.write("\n")
