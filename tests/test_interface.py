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
        assert sorted([node.display for node in nodes]) == ["Root1", "Root2"]
        assert nodes[1].children[0].display == "Child"


if __name__ == "__main__":
    pytest.main()
