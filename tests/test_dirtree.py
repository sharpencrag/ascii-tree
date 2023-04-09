import pytest
from pathlib import Path
from ascii_tree import render, renderable_dir_tree

this_dir = Path(__file__).parent / "fixtures"
root_path = this_dir / "root_dir"


def test_renderable_dir_tree_recursive_true():
    root = renderable_dir_tree(root_path)

    expected_output = (
        "root_dir /\n"
        "├─ child_dir_one /\n"
        "│  ├─ grandchild_dir_one /\n"
        "│  │  └─ great_grandchild_file_one.txt\n"
        "│  └─ grandchild_file_one.txt\n"
        "└─ child_dir_two /\n"
        "   ├─ grandchild_dir_two /\n"
        "   │  └─ great_grandchild_file_two.txt\n"
        "   └─ grandchild_file_two.txt\n"
    )

    assert render(root) == expected_output


def test_renderable_dir_tree_recursive_false():
    root = renderable_dir_tree(str(root_path), recursive=False)

    expected_output = (
        "root_dir /\n" "├─ child_dir_one / ...\n" "└─ child_dir_two / ...\n"
    )

    assert render(root) == expected_output


def test_renderable_dir_tree_max_depth():
    root = renderable_dir_tree(str(root_path), max_depth=2)

    expected_output = (
        "root_dir /\n"
        "├─ child_dir_one /\n"
        "│  ├─ grandchild_dir_one / ...\n"
        "│  └─ grandchild_file_one.txt\n"
        "└─ child_dir_two /\n"
        "   ├─ grandchild_dir_two / ...\n"
        "   └─ grandchild_file_two.txt\n"
    )

    assert render(root) == expected_output


def test_renderable_dir_tree_ellipsis_after_max_depth_false():
    root = renderable_dir_tree(
        str(root_path), max_depth=2, ellipsis_after_max_depth=False
    )

    expected_output = (
        "root_dir /\n"
        "├─ child_dir_one /\n"
        "│  ├─ grandchild_dir_one /\n"
        "│  └─ grandchild_file_one.txt\n"
        "└─ child_dir_two /\n"
        "   ├─ grandchild_dir_two /\n"
        "   └─ grandchild_file_two.txt\n"
    )

    assert render(root) == expected_output


def test_renderable_dir_tree_slash_after_dir_false():
    root = renderable_dir_tree(str(root_path), slash_after_dir=False)

    expected_output = (
        "root_dir\n"
        "├─ child_dir_one\n"
        "│  ├─ grandchild_dir_one\n"
        "│  │  └─ great_grandchild_file_one.txt\n"
        "│  └─ grandchild_file_one.txt\n"
        "└─ child_dir_two\n"
        "   ├─ grandchild_dir_two\n"
        "   │  └─ great_grandchild_file_two.txt\n"
        "   └─ grandchild_file_two.txt\n"
    )

    assert render(root) == expected_output


if __name__ == "__main__":
    pytest.main()
