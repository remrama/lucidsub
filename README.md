# lucidsub

Project exploring [r/LucidDreaming](https://www.reddit.com/r/LucidDreaming/) for expressions of positive and negative experiences with lucid dreaming.


## Code/file descriptions

### Non-linear files

* `config.py` is where things like the data directory are specified
* `guideline.md` has the detailed descriptions of all themes

### Linear files

```bash
# grab r/LucidDreaming posts from reddit
python scrape_reddit.py                                 # ==> DATA_DIR/r-LucidDreaming_<timestamp>.csv

# draw a plot of post frequency over time
python plot_reddit.py                                   # ==> RESULTS_DIR/plots/reddit-postfrequency.png

# clean up a bit and reduce to 200
python clean_reddit.py --month April                    # ==> DATA_DIR/r-LucidDreaming_2019April+200.csv
python clean_reddit.py --month July                     # ==> DATA_DIR/r-LucidDreaming_2019July+200.csv

# convert initial reddit download from csv to jsonl
# (for uploading to Doccano)
python csv2jsonl.py  --month April                      # ==> DATA_DIR/r-LucidDreaming_2019April+200.jsonl
python csv2jsonl.py  --month July                       # ==> DATA_DIR/r-LucidDreaming_2019July+200.jsonl
```

--> leave code land and annotate posts on Doccano

```bash
# convert Doccano ratings to usable csv
python doccano2csv.py --version 1                       # ==> RESULTS_DIR/doccano-postXtheme_v1.csv
                                                        # ==> RESULTS_DIR/doccano-postXthemecoder_v1.csv
python doccano2csv.py --version 2                       # ==> RESULTS_DIR/doccano-postXtheme_v2.csv
                                                        # ==> RESULTS_DIR/doccano-postXthemecoder_v2.csv

# visualize how often coders (dis)agreed
python plot-agreement_postXtheme.py --version 1         # ==> RESULTS_DIR/doccano-postXtheme_v1.png
python plot-agreement_postXtheme.py --version 2         # ==> RESULTS_DIR/doccano-postXtheme_v2.png
python plot-agreement_postXthemeXcoder.py --version 1   # ==> RESULTS_DIR/doccano-postXthemeXcoder_v1.png
python plot-agreement_postXthemeXcoder.py --version 2   # ==> RESULTS_DIR/doccano-postXthemeXcoder_v2.png

# export a csv with only disagreements, for discussion
python find_disagreements.py --version 1                # ==> RESULTS_DIR/doccano-disagreements2solve_v1.csv
python find_disagreements.py --version 2                # ==> RESULTS_DIR/doccano-disagreements2solve_v2.csv
```

--> leave code land and resolve disputes in excel

```bash
# export the final totals in csv and png
python total_counts.py                                  # ==> RESULTS_DIR/themes-total_counts.csv
                                                        # ==> RESULTS_DIR/plots/themes-total_counts.png

# export the highlighted sections to browse for examples
python highlights_table.py                              # ==> RESULTS_DIR/themes-highlights_table.csv

# export some descriptive values to include in Results text
python theme_descriptives.py                            # ==> RESULTS_DIR/themes-descriptives.csv
                                                        # ==> RESULTS_DIR/themes-descriptives.json

# export a plot and stats comparing the frequency of pos-only vs neg-only
python analysis-valence                                 # ==> RESULTS_DIR/plots/valence.png

# generate jsonl file of all themed/surviving posts
python csv2jsonl-themed.py                              # ==> RESULTS_DIR/themed_posts.jsonl
```

--> leave code land and back to Doccano for a few more ratings

* Rate each post as having either high or "little-to-no" dream control (or not enough info).
* Rate each post as containing a dream experience or not.

```bash
python analysis-valenceXvar.py --var control            # ==> RESULTS_DIR/plots/valenceXcontrol.png
                                                        # ==> RESULTS_DIR/valenceXcontrol_chi2-freq.csv
                                                        # ==> RESULTS_DIR/valenceXcontrol_chi2-stat.csv
python analysis-valenceXvar.py --var ldexp              # ==> RESULTS_DIR/plots/valenceXldexp.png
                                                        # ==> RESULTS_DIR/valenceXldexp_chi2-freq.csv
                                                        # ==> RESULTS_DIR/valenceXldexp_chi2-stat.csv
```
