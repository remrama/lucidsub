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

###############################################
##  manually code/annotate posts on Doccano  ##
###############################################

# convert Doccano ratings to usable csv
python doccano2csv.py

# visualize how often coders (dis)agreed
python plot-agreement_postXtheme.py
python plot-agreement_postXthemeXcoder.py

# export a csv with only disagreements, for discussion
python find_disagreements.py
```