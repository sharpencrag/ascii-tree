from __future__ import annotations
import typing as t
import typing_extensions as te
from pathlib import Path

from ascii_tree import styles

T = t.TypeVar("T")


class Renderable(te.Protocol):
    display: str
    children: t.MutableSequence[Renderable]


class TextRenderNode:
    """Basic tree node for use with render_tree."""

    def __init__(
        self,
        display: str,
        children: t.Optional[t.MutableSequence[TextRenderNode]] = None,
    ):
        self.display: str = display
        self.children: t.MutableSequence[TextRenderNode] = (
            children if children is not None else []
        )


def renderable(
    obj: T,
    display_attr: t.Optional[str] = None,
    display_method: t.Optional[t.Callable[[], str]] = None,
    display_function: t.Optional[t.Callable[[T], str]] = None,
    children_attr: t.Optional[str] = None,
    children_method: t.Optional[t.Callable] = None,
    children_function: t.Optional[t.Callable[[T], str]] = None,
) -> TextRenderNode:
    """Create a TextRenderNode interface for a tree-structured object.

    Args:
        obj: The object to create a TextRenderNode interface for.
        display_attr: The attribute of the object to use as the display text.
        display_method: The method of the object to call to get the display text.
            Ignored if `display_attr` is provided.
        children_attr: An attribute name used to obtain the children of the
            object.
        children_method: A method used to obtain the children of the object.
            Ignored if `children_attr` is provided.

    If no attr or method is provided for either display or children, we'll
    default to obj.display and obj.children, respectively.

    """

    # check for whoopsies
    if (
        (display_attr and display_method)
        or (children_attr and children_method)
        or (display_attr and display_function)
        or (children_attr and children_function)
        or (display_method and display_function)
        or (children_method and children_function)
    ):
        raise ValueError(
            "You must provide only interface: attr, method, or function."
        )

    display = _get_from_interface(
        obj, "display", display_attr, display_method, display_function
    )

    children = _get_from_interface(
        obj, "children", children_attr, children_method, children_function
    )

    renderable_children = [renderable(child) for child in children]

    return TextRenderNode(display=display, children=renderable_children)


def _get_from_interface(
    obj: T,
    default_attr: str,
    provided_attr: str | None,
    method: t.Callable | None,
    function: t.Callable[[T]] | None,
) -> t.Any:
    if provided_attr:
        return_value = getattr(obj, provided_attr)
    elif method:
        return_value = method()
    elif function:
        return_value = function(obj)
    else:
        try:
            return_value = getattr(obj, default_attr)
        except AttributeError as e:
            raise AttributeError(
                f"The object must have a '{default_attr}' attribute or "
                f"provide an interface attribute or function."
            ) from e
    return return_value


def renderable_from_parents(
    objs: t.Sequence[T],
    parent_attr: t.Optional[str] = None,
    parent_method: t.Optional[t.Callable] = None,
    is_root_callback: t.Optional[t.Callable[[T], bool]] = None,
    display_attr: t.Optional[str] = None,
    display_method: t.Optional[t.Callable] = None,
    display_function: t.Optional[t.Callable[[T], str]] = None,
) -> t.List[TextRenderNode]:
    """Build a renderable tree from objects with only "parent" references.

    Given a sequence of hierarchically-organized objects which only store
    references to their parents (bottom-up organization), this function will
    build trees of (top-down) TextRenderNodes.

    Note that this function always returns a list of top-level TextRenderNodes,
    even if there is only one root node.  This is meant to support the case
    where there are multiple roots in your given sequence.

    Args:
        objs: A sequence of objects to build the tree from.
        parent_attr: An attribute (as a string) that obtains the parent.
        parent_method: A method to call to get a parent object.
        is_root_callback: A function that takes an object and returns True if
            it is a root node.
        display_attr: The attribute of the object to use as the display text.
        display_method: Method to call to get display text for the node.
        display_function: Function takes an object and returns the display.
    """

    def get_parent(obj) -> T | None:
        # ancestor is defined below - this is a closure
        if ancestor is None:
            return None
        if is_root_callback and is_root_callback(ancestor):
            return None
        if parent_attr:
            return getattr(obj, parent_attr)
        elif parent_method:
            return parent_method(obj)
        else:
            return obj.parent

    def make_node(obj):
        return renderable(
            obj,
            display_attr=display_attr,
            display_method=display_method,
            display_function=display_function,
            children_method=lambda: list(),
        )

    node_dict: t.Dict[T, TextRenderNode] = dict()
    roots = set()
    for obj in objs:
        ancestor = obj
        while ancestor:
            if ancestor not in node_dict:
                node_dict[ancestor] = make_node(ancestor)
            parent = get_parent(ancestor)
            ancestor = parent

    visited = set()
    for obj in objs:
        ancestor = obj
        while ancestor:
            if ancestor in visited:
                break
            visited.add(ancestor)
            parent = get_parent(ancestor)
            if parent:
                node_dict[parent].children.append(node_dict[ancestor])
            else:
                roots.add(node_dict[ancestor])
            ancestor = parent

    return list(roots)


def renderable_dir_tree(
    path: t.Union[str, Path],
    recursive: bool = True,
    max_dir_depth: t.Optional[int] = None,
    dir_filter: t.Callable[[Path], bool] | None = None,
    max_file_count: t.Optional[int] = None,
    file_filter: t.Callable[[Path], bool] | None = None,
    slash_after_dir: bool = True,
    ellipsis_after_max_depth: bool = True,
    ellipsis_after_max_files: bool = True,
    skip_if_no_permission: bool = True,
) -> TextRenderNode:
    """Create a TextRenderNode tree from a given file system path.

    Args:
        path: The path to the directory to build the tree from.
        recursive: Whether to build the tree recursively.
            Defaults to True.
        max_dir_depth: The maximum depth to build the tree
            to. If not specified, the tree will be built to its full depth.
            Defaults to None.
        dir_filter: A callable that takes a Path object and returns True if
            the directory should be included in the tree. Defaults to None.
        max_file_count: The maximum number of files to include in the tree per
            directory. If not specified, all files will be included. Defaults
            to None.
        file_filter: A callable that takes a Path object and returns True if
            the file should be included in the tree. Defaults to None.
        slash_after_dir: Whether to add a forward slash after
            directories in the tree. Defaults to True.
        ellipsis_after_max_depth: Whether to add an ellipsis
            after the last directory in a path that reaches the maximum depth.
            Defaults to True.
        ellipsis_after_max_files: Whether to add an ellipsis after the last
            file in a directory that reaches the maximum file count. Defaults
            to True.
        skip_if_no_permission: Whether to skip adding a node to
            the tree if permission is denied to access it. Defaults to True.

    Returns:
    TextRenderNode: A tree node representing the file system tree rooted at the
        given path.

    Raises:
    PermissionError: If permission is denied to access a node in the file system
        tree and skip_if_no_permission is False.

    """
    if recursive is False:
        max_dir_depth = 1

    def _build_tree(
        node_path: Path,
        current_depth: int,
        max_depth: t.Optional[int],
        max_files: t.Optional[int],
        dir_filter: t.Callable[[Path], bool] | None = None,
        file_filter: t.Callable[[Path], bool] | None = None,
    ) -> TextRenderNode:
        """Recursively build a TextRenderNode tree from a given file system path."""

        # we've reached max_depth, so we need to stop
        children: t.List[TextRenderNode] = []
        if max_depth and current_depth >= max_depth:
            display = (
                node_path.name
                + (" /" * slash_after_dir)
                + (" ..." * ellipsis_after_max_depth)
            )
            return TextRenderNode(display=display, children=children)

        # Node is a directory, continue building the tree
        try:
            child_iter = node_path.iterdir()
        except PermissionError:
            if skip_if_no_permission:
                return TextRenderNode(
                    display=node_path.name
                    + f"[Permission Denied]{' /' * slash_after_dir}"
                )
            else:
                raise
        permission_error_on_child = False

        current_file_count = 0
        skipping_remaining_files = False
        for child_path in child_iter:
            # Current node is a file
            try:
                is_file = child_path.is_file()
            except PermissionError:
                permission_error_on_child = True
                continue
            if is_file:
                if skipping_remaining_files:
                    continue
                current_file_count += 1
                # We're at the max file count, so we need to stop
                if max_files and current_file_count > max_files:
                    # We do want an ellipsis!
                    if ellipsis_after_max_files:
                        children.append(TextRenderNode(display="..."))
                    # Skip the rest of the files in this directory
                    skipping_remaining_files = True
                    continue
                # Check the filter...
                if file_filter and not file_filter(child_path):
                    continue
                # Add the file to the tree
                children.append(TextRenderNode(display=child_path.name))
            else:
                # Current node is a directory
                if dir_filter and not dir_filter(child_path):
                    continue
                try:
                    child_node = _build_tree(
                        child_path,
                        current_depth + 1,
                        max_depth,
                        max_files,
                        dir_filter,
                        file_filter,
                    )
                except PermissionError:
                    permission_error_on_child = True
                    continue
                else:
                    children.append(child_node)
        if permission_error_on_child:
            if skip_if_no_permission:
                children.append(TextRenderNode(display="[Permission Denied]"))
            else:
                raise

        display = node_path.name + (" /" * slash_after_dir)
        return TextRenderNode(display=display, children=children)

    root_path = Path(path).resolve()
    return _build_tree(
        root_path,
        0,
        max_dir_depth,
        max_file_count,
        dir_filter,
        file_filter,
    )


def render(
    node: TextRenderNode,
    style: styles.TextRenderStyle = styles.solid_line_style,
    width: int = 1,
    spacing: int = 1,
) -> str:
    """Render a tree made up of TextRenderNodes as a multiline string.

    The TextRenderNode is not strictly required; any object with a `display`
    attribute and a `children` sequence attribute will work. (In later versions
    of Python, this will be annotated with a Protocol.)

    You can obtain a TextRenderNode by using the `renderable` function, which
    will create an interface for any tree-structured object.  Just supply an
    attribute name or method to map to the `display` and `children` attributes.

    Args:
        node: The root node of the tree to render.  If you need multiple roots,
            it's best to render them separately and then join the results.
        style: The style to use when rendering the tree.  If not provided, a
            solid line style will be used.
        width: The width of the horizontal lines in the tree. Defaults to 1.
        spacing: The number of spaces to use between the horizontal line
            and the node's display text. Defaults to 1.

    Protected Args:
        _prefix: The lefthand decoration to use when rendering the current node.
        _is_last_sibling: Whether the current node is the last child of its
            parent.
        _is_root: Whether the current node is the root of the tree.
    """
    return _recursive_render(
        node,
        style=style,
        width=width,
        spacing=spacing,
    )


def _recursive_render(
    node: TextRenderNode,
    style: styles.TextRenderStyle,
    width: int,
    spacing: int,
    _prefix: str = "",
    _is_last_sibling: bool = True,
    _is_root: bool = True,
) -> str:
    """See `render_tree`.

    This function only exists to hide the recursion arguments from the
    public API.
    """

    style = style if style else styles.solid_line_style
    children = node.children
    child_count = len(children)

    if _is_root:
        tree_repr = node.display + "\n"
        new_prefix = _prefix
    else:
        tree_repr = _prefix
        if _is_last_sibling:
            tree_repr = "".join(
                (
                    tree_repr,
                    style.corner,
                    (style.hline * width),
                    (" " * spacing),
                )
            )
            new_prefix = _prefix + " " * (width + spacing + 1)
        else:
            tree_repr = "".join(
                (
                    tree_repr,
                    style.tee,
                    (style.hline * width),
                    (" " * spacing),
                )
            )
            new_prefix = _prefix + style.vline + " " * (width + spacing)

        tree_repr += node.display + "\n"

    for i, child in enumerate(children):
        tree_repr += _recursive_render(
            child,
            style,
            width,
            spacing,
            new_prefix,
            i == child_count - 1,
            _is_root=False,
        )

    return tree_repr
