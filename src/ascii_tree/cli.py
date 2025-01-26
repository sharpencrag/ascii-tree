import argparse

from ascii_tree import renderable_dir_tree, render, styles

from pathlib import Path
import fnmatch


def main():
    parser = argparse.ArgumentParser(
        description="Generate and display an ASCII representation of a directory structure."
    )
    parser.add_argument(
        "path",
        type=str,
        help="The path to the directory to generate the tree for."
    )
    parser.add_argument(
        "--flat",
        action="store_false",
        dest="recursive",
        help="Do not build the tree recursively."
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Maximum depth to build the tree. Defaults to no limit."
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=None,
        help="Maximum number of files per directory. Defaults to no limit."
    )
    parser.add_argument(
        "--dir-pattern",
        type=str,
        default=None,
        help="Glob pattern to filter directories (e.g., 'subdir*')."
    )
    parser.add_argument(
        "--file-pattern",
        type=str,
        default=None,
        help="Glob pattern to filter files (e.g., '*.json')."
    )
    parser.add_argument(
        "--no-slash",
        action="store_false",
        dest="slash_after_dir",
        help="Do not add a trailing slash after directory names."
    )
    parser.add_argument(
        "--no-ellipsis-depth",
        action="store_false",
        dest="ellipsis_after_max_depth",
        help="Do not add ellipsis for directories exceeding max depth."
    )
    parser.add_argument(
        "--no-ellipsis-files",
        action="store_false",
        dest="ellipsis_after_max_files",
        help="Do not add ellipsis for files exceeding max count."
    )
    parser.add_argument(
        "--raise-on-permission-error",
        action="store_false",
        dest="skip_if_no_permission",
        help="Do not skip nodes where permission is denied; raise an error instead."
    )
    styles_ = list(styles.styles_dict.keys())
    parser.add_argument(
        "--style",
        type=str,
        default=styles_[0],
        choices=styles_,
        help="Rendering style for the tree. Defaults to 'solid_line_style'."
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1,
        help="Width of horizontal lines in the tree. Defaults to 1."
    )
    parser.add_argument(
        "--spacing",
        type=int,
        default=1,
        help="Spacing between horizontal lines and node display text. Defaults to 1."
    )

    args = parser.parse_args()

    # Convert dir_pattern and file_pattern arguments to callable functions
    def dir_filter(path: Path) -> bool:
        return fnmatch.fnmatch(path.name, args.dir_pattern) if args.dir_pattern else True

    def file_filter(path: Path) -> bool:
        return fnmatch.fnmatch(path.name, args.file_pattern) if args.file_pattern else True

    # Generate the directory tree
    try:
        tree = renderable_dir_tree(
            path=args.path,
            recursive=args.recursive,
            max_dir_depth=args.max_depth,
            dir_filter=dir_filter,
            max_file_count=args.max_files,
            file_filter=file_filter,
            slash_after_dir=args.slash_after_dir,
            ellipsis_after_max_depth=args.ellipsis_after_max_depth,
            ellipsis_after_max_files=args.ellipsis_after_max_files,
            skip_if_no_permission=args.skip_if_no_permission,
        )

        # Render the tree to an ASCII string
        style = styles.styles_dict[args.style]
        output = render(tree, style=style, width=args.width, spacing=args.spacing)

        print(output)
    except Exception as e:
        print(f"Error generating directory tree: {e}")
        raise

if __name__ == "__main__":
    main()
