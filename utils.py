"""A set of generally useful functions.
Most are used in multiple scripts.
"""

def load_config(as_object=True):
    """Loads the json configuration file.
    With as_object True, it gets return as a namespace,
    otherwise a dictionary. Namespace allows it to be
    accessed like config.data_dir instead of config["data_dir"].
    """
    import json
    from types import SimpleNamespace
    with open("./config.json", "r", encoding="utf-8") as jsonfile:
        if as_object:
            config = json.load(jsonfile, object_hook=lambda d: SimpleNamespace(**d))
        else:
            config = json.load(jsonfile)
    return config

# Load in the configuration file so it can be
# accessed easily with utils.Config within scripts.
Config = load_config()


def load_final_post_themes(config):
    """Get the final themes of each post, across both months/versions,
    after resolving last disagreements.
    """
    import pandas as pd
    from os.path import join as opj
    n_coders = len(config.coders)
    df_list = []
    for month in ["April", "July"]:
        import_basename1 = f"doccano-postXtheme_2019{month}.csv"
        import_basename2 = f"doccano-disagreements_2019{month}-DONE.xlsx"
        import_fullpath1 = opj(config.data_directory, "derivatives", import_basename1)
        import_fullpath2 = opj(config.data_directory, "source", import_basename2)
        df1 = pd.read_csv(import_fullpath1, index_col="post_id")
        df2 = pd.read_excel(import_fullpath2, index_col="post_id")
        # Binarize the original ratings to only keep posts from all coders.
        df1 = df1.eq(n_coders)
        # Handle (resolved) disagreement file.
        df2 = df2.loc[df2["keep"], ["theme", "keep"]].pivot(columns="theme"
            ).droplevel(0, 1).reindex_like(df1).fillna(False)
        # Merge them.
        df_ = df1 | df2
        # Append to list for concatenating.
        df_list.append(df_)
    return pd.concat(df_list)


def load_matplotlib_settings():
    """Load aesthetics I like.
    """
    from matplotlib.pyplot import rcParams
    rcParams["savefig.dpi"] = 600
    rcParams["interactive"] = True
    rcParams["font.family"] = "Times New Roman"
    # rcParams["font.sans-serif"] = "Arial"
    rcParams["mathtext.fontset"] = "custom"
    rcParams["mathtext.rm"] = "Times New Roman"
    rcParams["mathtext.cal"] = "Times New Roman"
    rcParams["mathtext.it"] = "Times New Roman:italic"
    rcParams["mathtext.bf"] = "Times New Roman:bold"
    rcParams["font.size"] = 8
    rcParams["axes.titlesize"] = 8
    rcParams["axes.labelsize"] = 8
    rcParams["axes.labelsize"] = 8
    rcParams["xtick.labelsize"] = 8
    rcParams["ytick.labelsize"] = 8
    rcParams["legend.fontsize"] = 8
    rcParams["legend.title_fontsize"] = 8


def no_leading_zeros(x, pos):
    """A custom tick formatter for matplotlib
    that will remove leading zeros in front of decimals.
    """
    val_str = "{:g}".format(x)
    if abs(x) > 0 and abs(x) < 1:
        return val_str.replace("0", "", 1)
    else:
        return val_str


def save_hires_copies(png_fname, skip_extensions=[]):
    """Saves out hi-resolution matplotlib figures.
    Assumes there is a "hires" subdirectory within the path
    of the filename passed in, which must be also be a png filename.
    """
    assert png_fname.endswith(".png"), f"Must pass a .png filename, you passed {png_fname}"
    import os
    from matplotlib.pyplot import savefig
    png_dir, png_bname = os.path.split(png_fname)
    hires_dir = os.path.join(png_dir, "hires")
    skip_extensions = [ "."+e if not e.startswith(".") else e for e in skip_extensions ]
    for ext in [".svg", ".eps", ".pdf"]:
        if ext not in skip_extensions:
            hires_bname = png_bname.replace(".png", ext)
            hires_fname = os.path.join(hires_dir, hires_bname)
            savefig(hires_fname)
