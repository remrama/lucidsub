import json
import matplotlib.pyplot as plt

plt.rcParams["savefig.dpi"] = 600
plt.rcParams["interactive"] = True
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Arial"
plt.rcParams["mathtext.fontset"] = "custom"
plt.rcParams["mathtext.rm"] = "Arial"
plt.rcParams["mathtext.it"] = "Arial:italic"
plt.rcParams["mathtext.bf"] = "Arial:bold"


DATA_DIR = "../data/20210822"
RESULTS_DIR = "../results"

POS_COLOR = "#4CAF50"
NEG_COLOR = "#F44336" 

CODERS = ["remym", "lsowin", "rraider", "hcaldas", "hadaweh"] #"cmader", "kkonkoly"]

with open("../code/labels.json", "r") as infile:
    THEMES = [ label["text"] for label in json.load(infile) ]
    n_themes = len(THEMES)
    n_pos_themes = THEMES.index("Sleep paralysis")
    n_neg_themes = n_themes - n_pos_themes
