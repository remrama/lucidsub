"""Draw a box&arrow diagram of the content analysis steps.
"""
import os
import graphviz
import utils


# Generate filenames, but without extensions (they get auto added).
export_fname = os.path.join(utils.Config.data_directory, "results", "method")
export_fname_hires = os.path.join(utils.Config.data_directory, "results", "hires", "method")


LABELS = {
    "A" : "Develop themes\nfrom prior research\nand r/LucidDreaming",
    "B" : "Raters code a\nsubset of posts\nfor thematic content",
    "C" : "Meet, discuss, and\nadjust themes based\non new insights",
}

# Initiate the graph.
g = graphviz.Digraph(engine="dot")

# Set graph attributes.
g.attr(
    rankdir="LR", # flow left-to-right
    ratio="auto", # aspect ratio (drawing height/drawing width) for the drawing
    resolution="600", # dpi
    ranksep=".5", nodesep=".5", # https://stackoverflow.com/a/44735237
    fontsize="10",
)

# Set node attributes.
g.attr("node",
    shape="box",
    style="rounded",
    width="1.5",
    height=".5",
    fontsize="10",
)

# Set edge attributes.
g.attr("edge",
    arrowsize="1.0",
    penwidth="1.0",
    arrowhead="normal",
)


# Draw nodes and edges.
for k, v in LABELS.items():
    g.node(k, label=v)#, xlabel=k)
g.edge("A", "B", weight="1")
g.edge("B", "C", weight="1")
g.edge("C", "B", weight="0", label="Repeat as needed")


# Export.
g.render(filename=export_fname, format="png", cleanup=True, view=False)
g.render(filename=export_fname_hires, format="pdf", cleanup=True, view=False)
