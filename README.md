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

# convert initial reddit download from csv to jsonl for Doccano
python csv2jsonl.py
```