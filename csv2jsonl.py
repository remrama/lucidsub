"""Load in cleaned up r/LucidDreaming data
and export as jsonl file for Doccano import.
"""
import os
import json
import pandas as pd

# IMPORT_FNAME = r"C:/Users/sowin/<project_folder>/r-LucidDreaming_200.csv"
# EXPORT_FNAME = r"C:/Users/sowin/<project_folder>/r-LucidDreaming_200.jsonl"
IMPORT_FNAME = "/Users/remy/Google Drive/projects/lucidsub/data/r-LucidDreaming_2020April+200.csv"
EXPORT_FNAME = "/Users/remy/Google Drive/projects/lucidsub/data/r-LucidDreaming_2020April+200.jsonl"

# load data
df = pd.read_csv(IMPORT_FNAME, encoding="utf-8")

# open a file that will continuously be written into
with open(EXPORT_FNAME, "w", encoding="utf-8") as outfile:

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
