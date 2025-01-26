import pytest
from ascii_tree import TextRenderNode, renderable, renderable_from_parents


class TestTextRenderNode:
    def test_initialization(self):
        node = TextRenderNode("Test")
        assert node.display == "Test"
        assert node.children == []


class TestRenderable:
    class DummyObject:
        def __init__(self, name, children):
            self._name = name
            self._children = children

        def children_method(self):
            return self._children

        def display_method(self):
            return self._name

    class DummyWithDefaultAttrs:
        def __init__(self, name, children):
            self.display = name
            self.children = children

    def test_renderable_fallbacks(self):
        obj = self.DummyWithDefaultAttrs("Test", [])
        node = renderable(obj)
        assert node.display == "Test"
        assert node.children == []

    def test_renderable_fails_with_no_children_fallback(self):
        obj = self.DummyObject("Test", [])
        with pytest.raises(AttributeError):
            renderable(obj, display_attr="_name")

    def test_renderable_with_attribute(self):
        obj = self.DummyObject("Test", [])
        node = renderable(obj, display_attr="_name", children_attr="_children")
        assert node.display == "Test"
        assert node.children == []

    def test_renderable_with_method(self):
        obj = self.DummyObject("Test", [])
        node = renderable(
            obj, display_method=obj.display_method, children_method=obj.children_method
        )
        assert node.display == "Test"
        assert node.children == []

    def test_renderable_with_function(self):
        children = [self.DummyWithDefaultAttrs("Bar", []), self.DummyWithDefaultAttrs("Baz", [])]
        expected_names = ["Bar", "Baz"]
        def display_func(obj):
            return "Foo"
        def children_func(obj):
            return children
        obj = self.DummyWithDefaultAttrs("Test", [])
        node = renderable(
            obj, display_function=display_func,
            children_function=children_func, # type: ignore - don't need typed return
        )
        assert node.display == "Foo"
        assert [c.display for c in node.children] == expected_names

    def test_renderable_with_oddball_callables(self):
        obj = self.DummyObject("Test", [])
        node = renderable(
            obj, display_method=lambda: "Foo", children_method=lambda: []
        )
        assert node.display == "Foo"
        assert node.children == []


class TestRenderableFromParents:
    class DummyObject:
        def __init__(self, name, parent=None):
            self.name = name
            self.parent = parent

    class DummyWithDifferentParentSentinel:
        # This tests the ability to use a callback to determine if a node is root
        def __init__(self, name, parent=None):
            self.name = name
            self.parent = parent or 5

        def is_root(self):
            return self.parent == 5

    def test_single_root(self):
        obj1 = self.DummyObject("Root")
        obj2 = self.DummyObject("Child", parent=obj1)
        nodes = renderable_from_parents(
            [obj1, obj2],
            parent_attr="parent",
            display_attr="name",
        )
        assert len(nodes) == 1
        assert nodes[0].display == "Root"
        assert nodes[0].children[0].display == "Child"

    def test_multiple_roots(self):
        obj1 = self.DummyObject("Root1")
        obj2 = self.DummyObject("Root2")
        obj3 = self.DummyObject("Child", parent=obj2)
        nodes = renderable_from_parents(
            [obj1, obj2, obj3],
            parent_attr="parent",
            display_attr="name",
        )
        assert len(nodes) == 2
        nodes = sorted(nodes, key=lambda node: node.display)
        assert [node.display for node in nodes] == ["Root1", "Root2"]
        assert nodes[1].children[0].display == "Child"

    def test_root_callback(self):
        obj = self.DummyWithDifferentParentSentinel("Root")
        obj2 = self.DummyWithDifferentParentSentinel("Child", parent=obj)
        nodes = renderable_from_parents(
            [obj2],
            parent_attr="parent",
            display_attr="name",
            is_root_callback=(lambda node: node.is_root()),
        )
        assert len(nodes) == 1
        assert nodes[0].display == "Root"
        assert nodes[0].children[0].display == "Child"


if __name__ == "__main__":
    pytest.main()
