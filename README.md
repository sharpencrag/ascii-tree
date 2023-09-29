# ascii-tree

(Yet another) ascii tree rendering utility!

There are a bunch existing solutions out there for drawing directory structures in ascii, but not many with the ability to draw non-filesystem object hierarchies.

`ascii-tree` provides an easy-to-use interface to display any tree-like data as a string.

## Drawing a Directory Tree
One batteries-included feature of `ascii-tree` is the ability to draw directory trees.

This also provides a good example of how you might customize rendering for custom tree data.

```python
import ascii_tree
tree = ascii_tree.renderable_dir_tree(
    "./tests/fixtures"
)
print(ascii_tree.render(tree))
```
Output:
```
fixtures /
└─ root_dir /
   ├─ child_dir_one /
   │  ├─ grandchild_dir_one /
   │  │  └─ great_grandchild_file_one.txt
   │  └─ grandchild_file_one.txt
   └─ child_dir_two /
      ├─ grandchild_dir_two /
      │  └─ great_grandchild_file_two.txt
      └─ grandchild_file_two.txt
```
By default, this will recurse until all directories and files are visited.
### Setting Traversal Depth
By providing a `max_depth` argument, you can only search directories up to a certain level of nesting:
```python
import ascii_tree
tree = ascii_tree.renderable_dir_tree(
    "./tests/fixtures",
    max_depth=2
)
print(ascii_tree.render(tree))
```
Output:
```
fixtures /
└─ root_dir /
   ├─ child_dir_one / ...
   └─ child_dir_two / ...
```
The slashes after directories and the ellipses (`...`) after max depth can be controlled with parameters on `renderable_dir_tree`.
```python
import ascii_tree
tree = ascii_tree.renderable_dir_tree(
    "./tests/fixtures",
    max_depth=2,
    slash_after_dir=False,
    ellipsis_after_max_depth=False
)
```
Output:
```
fixtures
└─ root_dir
   ├─ child_dir_one
   └─ child_dir_two
```
### Dealing with Permission Errors
Finally, if you are traversing files with mixed permission levels, it can be useful to skip files that would otherwise cause a `PermissionError` when access isn't allowed.  Use the
`skip_if_no_permission` parameter:
```python
import ascii_tree
tree = ascii_tree.renderable_dir_tree(
    "here/be/dragons",
    skip_if_no_permission=True
)
print(ascii_tree.render(tree))
```
Output:
```
dragons /
├─ pendor /
│  └─ yevaud.txt
├─ lonely_mountain [Permission Denied]
└─ westeros /
   └─ balereon.txt
```
## Building a Tree from Scratch

Trees can be built up from a chain of `TextRenderNode` instances.  `TextRenderNode` is extremely simple; just a `display` and a `children` attribute.

```python
import ascii_tree

grandchild = ascii_tree.TextRenderNode("grandchild")
grandchild_two = ascii_tree.TextRenderNode("grandchild_two")
child = ascii_tree.TextRenderNode("child", children=[grandchild, grandchild_two])
root = ascii_tree.TextRenderNode("root", children=[child]])

print(ascii_tree.render(root))
```

Output:
```
root
└─ child
   ├─ grandchild
   └─ grandchild_two
```

## Making a Custom ASCII-Tree Interface

Unless you're very lucky, your data *probably* doesn't have `display` and `children` attributes.  So we'll need to use an interface!

Let's assume you've got your business data in a class like so:
```python
class YourClass:
    def __init__(self, name, child_names=None):
        self.name = name
        self.child_names = child_names or []

    def get_children(self):
        return [YourClass(name) for name in self.child_names]
```
We'll want to map the `name` attribute to `display`, and the `get_children` method to `children`.
```python
import ascii_tree

obj = YourClass(name="root", children=["one", "two"])

node = ascii_tree.renderable(
    obj, display_attr="name", children_method=obj.get_children
)

print(ascii_tree.render(node))
```
Output:
```
root
├─ one
└─ two
```

The `renderable` function allows you to specify an attribute or a method for both `display` and `children`

## Parent-Only Interface

Oftentimes, hierarchically-organized objects only contain references to their parents instead of their children.  In that case, we need to do a little more transformation in order to build the renderable tree.

```python
class MyObjectType:
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

root = MyObjectType("root", parent=None)
child = MyObjectType("child_one", parent=root)
grandchild = MyObjectType("grandchild_one", parent=child)
```
In this case, we need to build the tree *upwards* from the leaf nodes (the grandchildren).
To do so, pass the leaf-level objects in the tree to the `renderable_from_parents` function:

```python
import ascii_tree
tree = ascii_tree.renderable_from_parents(
    [grandchild],
    parent_attr="parent"
)
print(ascii_tree.render(tree[0]))
```
By default, nodes are considered to be "root-level" if they return `None` from either `parent_attr` or `parent_method`.

If your system handles root status differently, you can pass in a callback function,
`is_root_callback`, to `renderable_from_parents` to override this behavior.  `is_root_callback` takes a single argument, the node in question, and should return `True` if the node is a root node, and `False` otherwise.

Note that `renderable_from_parents` always **returns a list** -- this is to ensure that
data with multiple root nodes are supported.

Output:
```
root
└─ child
   └─ grandchild
```

## Rendering Styles

`ascii-tree` currently provides three styles of rendering:
### Solid Line Style
```python
render(tree, style=styles.solid_line_style)
```
```
root
├─ child_one
│  ├─ grandchild_one
│  │  ├─ great_grandchild_one
│  │  └─ great_grandchild_two
│  └─ grandchild_two
│     ├─ great_grandchild_three
│     └─ great_grandchild_four
└─ child_two
```
### Basic Style
```python
render(tree, style=styles.basic_style)
```
```
root
+- child_one
|  +- grandchild_one
|  |  +- great_grandchild_one
|  |  +- great_grandchild_two
|  +- grandchild_two
|     +- great_grandchild_three
|     +- great_grandchild_four
+- child_two
```
### Clean Style
```python
render(tree, style=styles.clean_style)
```
```
root
· child_one
  · grandchild_one
    · great_grandchild_one
    · great_grandchild_two
  · grandchild_two
    · great_grandchild_three
    · great_grandchild_four
· child_two
```
