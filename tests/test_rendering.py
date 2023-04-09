import pytest

from ascii_tree import (
    render,
    TextRenderNode,
)

from ascii_tree.styles import (
    solid_line_style,
    clean_style,
    basic_style,
)


class TestTextRenderNode:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.root = TextRenderNode("root")
        child_one = TextRenderNode("child_one")
        child_two = TextRenderNode("child_two")
        grandchild_one = TextRenderNode("grandchild_one")
        grandchild_two = TextRenderNode("grandchild_two")
        great_grandchild_one = TextRenderNode("great_grandchild_one")
        great_grandchild_two = TextRenderNode("great_grandchild_two")
        great_grandchild_three = TextRenderNode("great_grandchild_three")
        self.root.children.extend([child_one, child_two])
        child_one.children.extend([grandchild_one, grandchild_two])
        grandchild_one.children.extend(
            [great_grandchild_one, great_grandchild_two, great_grandchild_three]
        )

    def test_render_tree_solid_style(self):
        expected_output = (
            "root\n"
            "├─ child_one\n"
            "│  ├─ grandchild_one\n"
            "│  │  ├─ great_grandchild_one\n"
            "│  │  ├─ great_grandchild_two\n"
            "│  │  └─ great_grandchild_three\n"
            "│  └─ grandchild_two\n"
            "└─ child_two\n"
        )

        assert render(self.root, solid_line_style) == expected_output

    def test_render_tree_clean_style(self):
        expected_output = (
            "root\n"
            "· child_one\n"
            "  · grandchild_one\n"
            "    · great_grandchild_one\n"
            "    · great_grandchild_two\n"
            "    · great_grandchild_three\n"
            "  · grandchild_two\n"
            "· child_two\n"
        )

        assert render(self.root, clean_style) == expected_output

    def test_render_tree_basic_style(self):
        expected_output = (
            "root\n"
            "+- child_one\n"
            "|  +- grandchild_one\n"
            "|  |  +- great_grandchild_one\n"
            "|  |  +- great_grandchild_two\n"
            "|  |  +- great_grandchild_three\n"
            "|  +- grandchild_two\n"
            "+- child_two\n"
        )

        assert render(self.root, basic_style) == expected_output


if __name__ == "__main__":
    pytest.main()
