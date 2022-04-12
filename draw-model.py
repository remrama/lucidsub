"""Draw a box&arrow diagram of the process model.
"""
import os
import graphviz
import utils


# Generate filenames, but without extensions (they get auto added).
export_fname = os.path.join(utils.Config.data_directory, "results", "model")
export_fname_hires = os.path.join(utils.Config.data_directory, "results", "hires", "model")

# Pull out colors from configuration for convenience.
pos_color = utils.Config.colors.positive
neg_color = utils.Config.colors.negative

GRAY = "gray92"

# Initiate the graph.
g = graphviz.Digraph("test", filename="./test", engine="dot")

# Set graph attributes.
g.attr(
    resolution="600", # dpi
    ratio="auto", # aspect ratio
    rankdir="LR", # flow direction
    ranksep=".4", # separation left/right *https://stackoverflow.com/a/44735237
    nodesep=".2", # separation up/down
    compound="true", # allow edges between clusters/subgraphs
    fontcolor="black",
    fontsize="10",
    # label="Lucid Dreaming Induction\nProcess Model",
)

# Set node attributes.
g.attr("node",
    shape="box",
    style="rounded,filled",
    color="black", # border
    fillcolor=GRAY,
    width=".8", # prevents auto-sizing so they're all the same
    height=".5", # prevents auto-sizing so they're all the same
    fontsize="10",
)

# Set edge attributes.
g.attr("edge",
    penwidth="1.0",
    arrowhead="open",
    arrowsize="1",
)


######################## Set up the legend.

# Create an invisible node sequence to create space for the legend.
# g.node("L1", style="invis")
g.node("L2")
g.node("L3")
# Draw legend as a subgraph.
with g.subgraph(name="cluster_0") as s:
    s.attr(label="", style="invis")
    s.attr("node", fontsize="8", height="0", width="0")
    s.node("L2", label="Positive\nexperience", fillcolor=pos_color)
    s.node("L3", label="Negative\nexperience", fillcolor=neg_color)
# Connect them all (invisibly) so they form a straight line.
# g.edge("L1", "L2", style="invis")
# g.edge("L2", "L3", style="invis")



######################## Generate the main section of interest.

# Start with first node.
g.node("A1", label="Lucid dream\ninduction attempt", fillcolor="white")

# Create subgraphs for the middle sections so they stack on top of each other.
# ***THE NAME OF THE SUBGRAPHS IMPACTS FORMATTING (STAY WITH cluster_<i>)***
with g.subgraph(name="cluster_1") as s:
    s.attr(rank="same", label="Induction\nsuccess", style="rounded,filled", fillcolor=GRAY)
    s.node("B1", label="Attain\nlucidity", fillcolor=pos_color)
    s.node("B2", label="Failed\nattempt", fillcolor=neg_color)
with g.subgraph(name="cluster_2") as s:
    s.attr(rank="same", label="Dream\ncontrol", style="rounded,filled", fillcolor=GRAY)
    s.node("C1", label="High\ncontrol", fillcolor=pos_color)
    s.node("C2", label="Low\ncontrol", fillcolor=neg_color)

# End with the final waking benefit node.
g.node("D1", label="Waking\nbenefit", shape="doublecircle", fillcolor=pos_color)

# Connect the top nodes so they're straight.
g.edge("A1", "B1", arrowsize="1.2")
g.edge("B1", "C1", arrowsize="1.2")
g.edge("C1", "D1", arrowsize="1.2")

# Connect the bottom nodes at angles, with weight 0 so nothing is pulled down.
g.edge("A1", "B2", weight="0", style="dashed", arrowhead="tee")
g.edge("B1", "C2", weight="0", style="dashed", arrowhead="tee")


# Export.
g.render(filename=export_fname, format="png", view=False, cleanup=True)
g.render(filename=export_fname_hires, format="pdf", view=False, cleanup=True)
