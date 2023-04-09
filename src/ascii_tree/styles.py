from dataclasses import dataclass


__all__ = ["TextRenderStyle", "solid_line_style", "clean_style", "basic_style"]


@dataclass
class TextRenderStyle:
    """A set of decorations used to render a tree as text."""

    hline: str
    vline: str
    tee: str
    corner: str
    space: str


# solid style - standard ASCII representation of trees
"""
root
├─ child_one
│  ├─ grandchild_one
│  │  ├─ great_grandchild_one
│  │  └─ great_grandchild_two
│  └─ grandchild_two
│     ├─ great_grandchild_three
│     └─ great_grandchild_four
└─ child_two
"""


solid_line_style = TextRenderStyle(
    hline="─",
    vline="│",
    tee="├",
    corner="└",
    space=" ",
)


# clean style - no lines, just a small dot
"""
root
· child_one
  · grandchild_one
    · great_grandchild_one
    · great_grandchild_two
  · grandchild_two
    · great_grandchild_three
    · great_grandchild_four
· child_two
"""
clean_style = TextRenderStyle(
    hline="·",
    vline="",
    tee="",
    corner="",
    space=" ",
)


# basic style - uses only keyboard-friendly characters
"""
root
+- child_one
|  +- grandchild_one
|  |  +- great_grandchild_one
|  |  +- great_grandchild_two
|  +- grandchild_two
|     +- great_grandchild_three
|     +- great_grandchild_four
+- child_two
"""
basic_style = TextRenderStyle(
    hline="-",
    vline="|",
    tee="+",
    corner="+",
    space=" ",
)
