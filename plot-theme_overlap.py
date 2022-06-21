"""Visualizing the overlap between themes.
"""
import os
import numpy as np
import pandas as pd
import utils

import networkx as nx
import nxviz as nv 
from nxviz import annotate, highlights

import matplotlib.pyplot as plt
utils.load_matplotlib_settings()


export_basename = "themes-overlap.png"
export_fullpath = os.path.join(utils.Config.data_directory, "results", export_basename)

df = utils.load_final_post_themes(utils.Config)
palette = utils.load_config(as_object=False)["colors"]

Config = utils.load_config(as_object=False)
theme2valence = {}
for valence, theme_list in Config["themes"].items():
    for theme in theme_list:
        theme2valence[theme] = valence


#### Get the node order for circular plot.
#### Need a strange order to get the node
#### valence symmetrical across horizontal.
#### (this is pretty ugly but works)

# make a dataframe for sorting by theme and count
counts = df.sum().reset_index(name="count").rename(columns={"index":"theme"})
counts["valence"] = counts["theme"].map(theme2valence)
counts = counts.sort_values(["valence", "count"])
counts = counts.set_index("theme")
theme_order = counts.index.tolist()
weird_order = theme_order[7:] + theme_order[:5][::-1] + theme_order[5:7]
sort_map = { t: i for i, t in enumerate(weird_order) }


#### Generate a network graph to input to nxviz for plotting.

G = nx.Graph()
for theme in df:
    G.add_node(theme,
        valence=theme2valence[theme],
        n_posts=counts.loc[theme, "count"],
        color=palette[theme2valence[theme]],
        order=sort_map[theme])
    # Get the amount of connections for each other theme.
    connections = df[df[theme]].drop(columns=theme
        ).melt().query("value")["variable"].value_counts()
    # Add edges for solos.
    n_this_theme = df[theme].sum()
    # n_this_theme_with_another = connections.sum()
    n_this_theme_with_another = df[df[theme]].drop(columns=theme).any(axis=1).sum()
    n_this_theme_alone = n_this_theme - n_this_theme_with_another
    connections.loc[theme] = n_this_theme_alone
    # G.add_edge(col, col, weight=n_this_theme_alone)
    for other_theme, n_connections in connections.items():
        G.add_edge(theme, other_theme,
            n_posts=n_connections)



###### Define plotting variables.

FIGSIZE = (3.2, 2.5)
RADIUS = 5
LABEL_OFFSET = 0
AXIS_MAX = 7 # axis limits will be (-axis_max, +axis_max)
GRIDSPEC_KWARGS = dict(top=1.05, left=.22, right=.78)
MAX_EDGEWIDTH = 5


###### Generate node patches to draw.
node_table = nv.utils.node_table(G)
pos = nv.layouts.circos(node_table, # group_by="valence", # not necessary bc sorting
    sort_by="order", radius=RADIUS)
node_radius = nv.nodes.node_size(node_table, "n_posts") # applies sqrt
node_radius = node_radius.div(node_radius.max())
node_color = node_table["color"]
node_alpha = nv.nodes.transparency(node_table, alpha_by=None)
node_patches = nv.nodes.node_glyphs(node_table, pos,
    node_color=node_color, alpha=node_alpha,
    size=node_radius)

###### Generate edge patches to draw.
edge_table = nv.utils.edge_table(G)
edge_color = nv.edges.edge_colors(edge_table,
    nt=None, color_by=None, node_color_by=None)
edge_lw = nv.edges.line_width(edge_table, "n_posts")
# edge_lw = edge_lw.div(edge_lw.max())
edge_lw = edge_lw.map(np.sqrt)
edge_lw = edge_lw.div(edge_lw.max()).mul(MAX_EDGEWIDTH)
# lw = np.sqrt(et["edge_value"])
edge_alpha = nv.edges.transparency(edge_table, alpha_by=None)
edge_patches = nv.lines.circos(edge_table, pos,
    edge_color=edge_color, alpha=edge_alpha, lw=edge_lw,
    aes_kw={"fc": "none"})


###### Draw!

fig, ax = plt.subplots(figsize=FIGSIZE, gridspec_kw=GRIDSPEC_KWARGS)
for patch in node_patches:
    ax.add_patch(patch)
for patch in edge_patches:
    ax.add_patch(patch)


###### Text annotations

# Labels
annotate.circos_labels(G, #group_by="valence",
    sort_by="order", layout="standard", # node_center/standard/rotate/numbers
    radius=RADIUS, radius_offset=LABEL_OFFSET, ax=ax)

# Valence grouping
# annotate.circos_group(G, group_by="valence", radius=RADIUS, radius_offset=0, midpoint=True, ax=ax)
# ax.text(-.2, 1, "Negative themes", transform=ax.transAxes, ha="left", va="bottom")
# ax.text(1.2, 1, "Positive themes", transform=ax.transAxes, ha="right", va="bottom")
ax.text(0, 1, "Negative themes", transform=ax.transAxes,
    ha="center", va="bottom", weight="bold")
ax.text(1, 1, "Positive themes", transform=ax.transAxes,
    ha="center", va="bottom", weight="bold")


###### Aesthetics
ax.set_xlim(-AXIS_MAX, AXIS_MAX)
ax.set_ylim(-AXIS_MAX, AXIS_MAX)
ax.set_axis_off()
nv.plots.rescale(G)
nv.plots.aspect_equal()



###### Generate and draw legends.

n_posts_min = 1 #node_table["n_posts"].min()
n_posts_max = 70 #node_table["n_posts"].max()
n_posts_mid = 35 #round((n_posts_max-n_posts_min) / 2)

NODE_LEGEND_XBASE = -8
NODE_LEGEND_YBASE = -8
NODE_HANDLE_LABEL_OFFSET = 2
NODE_HANDLE_SPACING = 1.5 # horizontal space between handles

sizes = [n_posts_min, n_posts_mid, n_posts_max]
radii = [ (np.sqrt(s)/np.sqrt(n_posts_max)) for s in sizes ]
gaps = [ r + (0 if i==0 else radii[i-1]) for i, r in enumerate(radii) ]
cumgaps = np.cumsum(gaps)
xlocs = [ NODE_LEGEND_XBASE + i*NODE_HANDLE_SPACING + cumgaps[i] for i, r in enumerate(radii) ]
ylocs = [ NODE_LEGEND_YBASE for s in sizes ]
labels = [ f"{s}\nposts" for s in sizes ]

CIRCLE_KWARGS = dict(facecolor="gainsboro",
    linewidth=0, edgecolor="black", clip_on=False)
node_handles = [ plt.Circle(xy=(x, y), radius=r, label=l, **CIRCLE_KWARGS)
    for l, r, x, y in zip(labels, radii, xlocs, ylocs) ]
for patch in node_handles:
    ax.add_patch(patch)
    label = patch.get_label()
    x, y = patch.get_center()
    ax.text(x, y-NODE_HANDLE_LABEL_OFFSET, label,
        ha="center", va="center", linespacing=.8, clip_on=False)


###### Now the edge legend.
n_posts_min = 1 #edge_table["n_posts"][edge_table["n_posts"].ne(0)].min()
n_posts_max = 40 #edge_table["n_posts"].max()
n_posts_mid = 20 #round((n_posts_max-n_posts_min) / 2)

EDGE_LEGEND_XBASE = 3
EDGE_LEGEND_YBASE = NODE_LEGEND_YBASE
EDGE_HANDLE_LABEL_OFFSET = NODE_HANDLE_LABEL_OFFSET # space between handles and their labels
EDGE_HANDLE_SPACING = 1.5 # space between handles
EDGE_HANDLE_LENGTH = 1 # how "long" the lines in legend should be

sizes = [n_posts_min, n_posts_mid, n_posts_max]
linewidths = [ MAX_EDGEWIDTH*(np.sqrt(s)/np.sqrt(n_posts_max)) for s in sizes ]
xlocs = [ EDGE_LEGEND_XBASE + i*EDGE_HANDLE_SPACING + i*EDGE_HANDLE_LENGTH
    for i in range(len(sizes)) ]
ylocs = [ EDGE_LEGEND_YBASE for s in sizes ]
labels = [ f"{s}\npost" + ("s" if s>1 else "") for s in sizes ]

LINE2D_KWARGS = dict(solid_capstyle="butt", color="black", alpha=.1, markersize=0, clip_on=False)
edge_handles = [ plt.Line2D([x, x], [y-EDGE_HANDLE_LENGTH/2, y+EDGE_HANDLE_LENGTH/2],
        linewidth=lw, label=l, **LINE2D_KWARGS)
    for x, y, lw, l in zip(xlocs, ylocs, linewidths, labels) ]
for artist in edge_handles:
    ax.add_artist(artist)
    label = artist.get_label()
    x, y = artist.get_xydata().mean(axis=0)
    ax.text(x, y-EDGE_HANDLE_LABEL_OFFSET, label,
        ha="center", va="center", linespacing=.8, clip_on=False)



# Export.
plt.savefig(export_fullpath)
utils.save_hires_copies(export_fullpath, skip_extensions=["eps"])
plt.close()