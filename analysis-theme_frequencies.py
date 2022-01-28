"""Export a table of final positive and negative theme frequencies.
"""
import os
import pandas as pd
import utils

# I/O
export_basename = "themes-frequencies.csv"
export_fullpath = os.path.join(utils.Config.data_directory, "results", export_basename)

# Get the dataframes holding resolved/final theme frequencies.
df = utils.load_final_post_themes(utils.Config)

# Count up each theme's single total frequency.
freqs = df.sum().rename("frequency")

# Export table of frequency counts.
freqs.to_csv(export_fullpath, index_label="theme")
