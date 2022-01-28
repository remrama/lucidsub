# lucidsub

This is code for a project exploring the positive and negative experiences around lucid dreaming. It involves running a content analysis on posts scraped from the [r/LucidDreaming](https://www.reddit.com/r/LucidDreaming/) subreddit. The content analysis is qualitative/manual, so code here is for other steps, like scraping/cleaning the data, aggregating the content analysis output, statistics, and visualizations. 



## Code and file descriptions


### Non-linear files

* `config.json` is where constants like the data directory are specified.
* `utils.py` is where generally useful python functions are stored.
* `guideline.md` has detailed descriptions of all the final themes.


### Linear files

```bash
# Generate the data/results directory structure that all files expect.
python setup-directory_structure.py             # ==> data/source/
                                                # ==> data/derivatives/
                                                # ==> data/results/
                                                # ==> data/results/hires/

# Grab all r/LucidDreaming posts from Reddit.
python scrape-reddit.py                         # ==> data/source/r-LucidDreaming_<timestamp>.csv
                                                # ==> data/source/r-LucidDreaming_<timestamp>.pkl
```

**Manual step.** The output file from `scrape-reddit.py` includes a timestamp. Copy/paste that into the `config.json` configuration file, so other scripts can find it.

```bash
# Draw a plot of all-time r/LucidDreaming post frequency.
python plot-methods.py                          # ==> data/results/methods.png
                                                # ==> data/results/post_frequency.txt

# Clean up the Reddit data a bit and reduce it to 2 batches of 200 posts.
# Include a jsonl file with each output, for uploading to Doccano.
python clean-reddit.py --month april            # ==> data/derivatives/r-LucidDreaming_2019April+200.csv
                                                # ==> data/derivatives/r-LucidDreaming_2019April+200.jsonl
python clean-reddit.py --month july             # ==> data/derivatives/r-LucidDreaming_2019July+200.csv
                                                # ==> data/derivatives/r-LucidDreaming_2019July+200.jsonl
```

**Manual step.** Code posts on [Doccano](https://doccano.herokuapp.com/). Once finished, save the main Doccano output folders in the `data/source/` directory and rename them to `data/source/doccano-2019April` and `data/source/doccano-2019July`.

```bash
# Convert Doccano ratings to useful csv files.
python doccano2csv.py --month april             # ==> data/derivatives/doccano-postXtheme_2019April.csv
                                                # ==> data/derivatives/doccano-postXthemeXcoder_2019April.csv
                                                # ==> data/derivatives/doccano-disagreements_2019April.csv
python doccano2csv.py --month july              # ==> data/derivatives/doccano-postXtheme_2019July.csv
                                                # ==> data/derivatives/doccano-postXthemeXcoder_2019July.csv
                                                # ==> data/derivatives/doccano-disagreements_2019July.csv

# Visuale how often coders (dis)agree.
python plot-postXtheme.py --month april         # ==> data/results/doccano-postXtheme_2019April.png
python plot-postXtheme.py --month july          # ==> data/results/doccano-postXtheme_2019July.png
python plot-postXthemeXcoder.py --month april   # ==> data/results/doccano-postXthemeXcoder_2019April.png
python plot-postXthemeXcoder.py --month july    # ==> data/results/doccano-postXthemeXcoder_2019July.png
```

**Manual step.** Leave code and resolve final disputes. Save as `data/source/doccano-disagreements_2019April-DONE.xlsx` and `data/source/doccano-disagreements_2019July-DONE.xlsx`.

```bash
# Export table and visualization of final theme frequencies (across both versions/months).
python analysis-theme_frequencies.py            # ==> data/results/themes-frequencies.csv
python plot-theme_frequencies.py                # ==> data/results/themes-frequencies.png

# Compare frequencies of *only* positive and only negative posts, and visualize.
# And generate 2 other files related to these "only" posts for later use.
python analysis-theme_valence.py                # ==> data/results/themes-valence.csv
                                                # ==> data/derivatives/themes-valence.json
                                                # ==> data/derivatives/themes-valence.jsonl
python plot-theme_valence.py                    # ==> data/results/themes-valence.png

# Generate some descriptive values for each theme and the overall corpus.
# export some descriptive values to include in Results text
python analysis-descriptives.py                 # ==> data/results/themes-descriptives.csv
                                                # ==> data/results/corpus-descriptives.csv

# Export a table with all highlighted/"themed" content to browse for examples.
python generate_highlights_table.py             # ==> data/derivatives/themes-highlights.csv
```

**Manual step.** Code posts on [Doccano](https://doccano.herokuapp.com/). Once finished, save the main Doccano output folders in the `data/source/` directory and rename them to `data/source/doccano-control` and `data/source/doccano-lucidity`.

```bash
python analysis-valenceXattributes.py           # ==> data/results/themes-valenceXattribute_freqs.csv
                                                # ==> data/results/themes-valenceXattribute_stats.csv

python plot-valenceXattribute.py -a control     # ==> data/results/themes-valenceXattribute_control.png
python plot-valenceXattribute.py -a lucidity    # ==> data/results/themes-valenceXattribute_lucidity.png
```
