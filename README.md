# lucidsub

Project exploring [r/LucidDreaming](https://www.reddit.com/r/LucidDreaming/) for expressions of positive and negative experiences with lucid dreaming.


## Code/file descriptions

### Non-linear files

* `config.py` is where things like the data directory are specified
* `guideline.md` has the detailed descriptions of all themes

### Linear files

```bash
# grab r/LucidDreaming posts from reddit
python scrape_reddit.py

# clean up a bit and reduce to 200
python clean_reddit.py

# convert initial reddit download from csv to jsonl
# (for uploading to Doccano)
python csv2jsonl.py
```

--> leave code land and annotate posts on Doccano

```bash
# convert Doccano ratings to usable csv
python doccano2csv.py --version 1
python doccano2csv.py --version 2

# visualize how often coders (dis)agreed
python plot-agreement_postXtheme.py --version 1
python plot-agreement_postXtheme.py --version 2
python plot-agreement_postXthemeXcoder.py --version 1
python plot-agreement_postXthemeXcoder.py --version 2

# export a csv with only disagreements, for discussion
python find_disagreements.py --version 1
python find_disagreements.py --version 2
```

--> leave code land and resolve disputes in excel

```bash
# export the final totals in csv and png
python total_counts.py

# export the highlighted sections to browse for examples
python highlights_table.py

# export some descriptive values to include in Results text
python theme_descriptives.py

# generate jsonl file of all themed/surviving posts
python csv2jsonl-themed.py
```
