from config import *

import os
import numpy as np
import pandas as pd

import_fname1 = os.path.join(RESULTS_DIR, "irr_pairs.csv")
import_fname2 = os.path.join(RESULTS_DIR, "irr_multi.csv")

df1 = pd.read_csv(import_fname1, index_col="theme")
df2 = pd.read_csv(import_fname2, index_col="theme")

fig, axes = plt.subplots(n_themes, figsize=(6,6),
    constrained_layout=True, sharex=True, sharey=True)

# for ax in axes:
#     if not ax.is_last_row():
#         ax.axis("off")

for th, ax in zip(THEMES, axes):
    fleiss = df2.loc[th, "fleiss_kappa"]

    ax.bar(-1, fleiss)

    # get all "permuted" cohen kappas
    for i, c in enumerate(["A", "B", "C", "D", "E"]):
        theme_data = df1.loc[th]
        cohens = theme_data.loc[
            theme_data.apply(lambda row: c in row.values, axis=1),
            "cohen_kappa"].values
        ax.scatter(np.repeat(i, cohens.size), cohens, c="gray", s=3)

    cohen_combos = df1.loc[th].values
    # for *coders, alpha in cohen_combos:
    #     # each alpha is getting plotted in 2 separate sections

    # np.nanmean(cohen_combos[:,2].astype(float))
    ax.set_ybound(upper=1)





