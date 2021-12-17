"""trying out a box and arrow diagram in matplotlib
"""
import os
import config as c

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
plt.rcParams["savefig.dpi"] = 600
plt.rcParams["interactive"] = True
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Arial"


export_fname = os.path.join(c.RESULTS_DIR, "plots", "methods-content_analysis.png")


FIGSIZE = (2.8, 3)

_, ax = plt.subplots(figsize=FIGSIZE,
    gridspec_kw=dict(top=1, bottom=0, left=0, right=1))

# draw 3 boxes in a row
leftest = .05
highest = .98
boxwidth = .75
boxheight = .25
boxgap = .1
texts = [
    ("Step 1:\n"
    + "Develop positive and negative\n"
    + "themes based on existing\n"
    + "literature and r/LucidDreaming"),

    ("Step 2:\n"
    + "Raters individually code 50\n"
    + "posts or the presence of\n"
    + "existing and novel themes"),

    ("Step 3:\n"
    + "Raters meet, discuss and\n"
    + "adjust based on disagreements\n"
    + "and novel insights"),
]
xpositions = [leftest] * 3
ypositions = [ highest - (i+1)*boxheight - i*boxgap for i in range(3) ]
boxstyle = "round, pad=0"
transform = ax.transAxes

arrowstyle = "Simple, tail_width=0.5, head_width=4, head_length=8"
arrow_kw = dict(arrowstyle=arrowstyle, color="k", lw=1)

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
# ax.axis("off")
left_txtbuff = .01

for txt, x, y in zip(texts, xpositions, ypositions):

    # easiest solution is to draw text and box at ONCE with a textbox
    # but it's tough to set the width of the box (it fits to text)
    # textbox_props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
    # t = ax.text(x, y, txt, transform=ax.transAxes,
    #     fontsize=10, va="bottom", ha="left",
    #     bbox=textbox_props)
    # bb = t.get_bbox_patch()

    # draw box
    bottomleft_xy = (x, y) # lower left corner of box
    rect = mpatches.FancyBboxPatch(
        bottomleft_xy,
        boxwidth, boxheight, facecolor="white",
        boxstyle=boxstyle, transform=transform)
    ax.add_patch(rect)

    # draw text
    text_x = x+left_txtbuff
    text_y = y+boxheight/2
    t = ax.text(text_x, text_y, txt,
        transform=ax.transAxes,
        fontsize=10, ha="left", va="center")


    # draw arrow
    if txt.startswith("Step 3"):
        # curved arrow going back up
        arrow_xy1 = (x+boxwidth, y+boxheight/2) # middle right of this box
        arrow_xy2 = (x+boxwidth, y+boxheight*1.5+boxgap) # middle right of next box
        arrow = mpatches.FancyArrowPatch(
            arrow_xy1, arrow_xy2,
            connectionstyle="arc3,rad=.5", **arrow_kw)
    else:
        arrow_xy1 = (x+boxwidth/2, y) # bottom of this box
        arrow_xy2 = (x+boxwidth/2, y-boxgap) # top of next box
        arrow = mpatches.FancyArrowPatch(
            arrow_xy1, arrow_xy2, **arrow_kw)
    ax.add_patch(arrow)

    # add extra text for step 4
    if txt.startswith("Step 3"):
        step4txt = "Repeat as needed"
        vert_x = x+boxwidth+.1 # some guessing to get past the curved arrow bump
        vert_y = y+boxheight+boxgap/2
        ax.text(vert_x, vert_y, step4txt,
            transform=ax.transAxes,
            rotation=270,
            fontsize=10, ha="left", va="center")



plt.savefig(export_fname)
plt.close()
