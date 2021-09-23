"""inter-rater reliability
"""
import os
import itertools

import numpy as np
import pandas as pd

import krippendorff
from statsmodels.stats import inter_rater


import utils


RESULTS_DIR = "../results"

data = utils.load_data()

df = utils.aggregate_codersXtheme(data)


alpha_scores = {}
kappa_scores = {}
kappaf_scores = {}

coders = df.index.get_level_values("coder").unique().tolist()

for theme, tdf in df.groupby("theme"):

    # extract the scores for only this subtheme
    postXcoder = tdf.T.values

    # get Cohen's kappa (2-coder score, so have to iterate)
    kappa_list = []
    pct_list = []
    for c1, c2 in itertools.combinations(coders, 2):
        # r1, r2 = stheme_ratings[[c1,c2]].T.values
        # r1, r2 = tdf.loc[pd.IndexSlice[:,[c1,c2]],:].values
        # k = cohen_kappa_score(r1, r2)
        # pct = np.mean(r1 == r2) # also grab pct agreement bc it's easy
        vals = tdf.loc[pd.IndexSlice[:,[c1,c2]],:].T.values
        contingency, _ = inter_rater.to_table(vals, bins=2)
        k = inter_rater.cohens_kappa(contingency, return_results=False)
        kappa_list.append(dict(coder1=c1, coder2=c2, cohen_kappa=k))#, pct=pct))
    kappa_scores[theme] = kappa_list

    # get Fleiss's kappa (multi-coder score)
    postXcats, _ = inter_rater.aggregate_raters(postXcoder, n_cat=2)
    kappa_f = inter_rater.fleiss_kappa(postXcats, method="fleiss")
    kappaf_scores[theme] = kappa_f

    # get Krippendorff's alpha (multi-coder score)
    rating_lists = [ list(x.flatten()) for x in np.hsplit(postXcoder, len(coders)) ]
    alpha = krippendorff.alpha(reliability_data=rating_lists,
        level_of_measurement="nominal")
    alpha_scores[theme] = alpha


# build kappa dataframe
kappa_df = pd.concat([ pd.DataFrame(scores, index=np.repeat(st,len(scores)))
        for st, scores in kappa_scores.items() ]
    ).rename_axis("theme"
    ).reset_index(
    ).set_index(["theme", "coder1", "coder2"]
    ).sort_index(
    ).reindex(utils.themes, level="theme")


# build alpha and fleiss kappa dataframes, which can be merged to 1
alpha_df = pd.DataFrame.from_dict(alpha_scores, orient="index"
    ).rename_axis("theme").rename(columns={0:"krippendorff_alpha"})
kappaf_df = pd.DataFrame.from_dict(kappaf_scores, orient="index"
    ).rename_axis("theme").rename(columns={0:"fleiss_kappa"})
multicoder_scores = alpha_df.join(kappaf_df, on="theme"
    ).reindex(utils.themes)


######################################################

# export
basic_fname = os.path.join(RESULTS_DIR, "irr_pairs.csv")
multi_fname = os.path.join(RESULTS_DIR, "irr_multi.csv")
kappa_df.round(3).to_csv(basic_fname, index=True, na_rep="NA")
multicoder_scores.round(3).to_csv(multi_fname, index=True, na_rep="NA")


