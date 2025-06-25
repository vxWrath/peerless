import pytest
from utility.namespace import Namespace

class TestNamespace:
    def test_init_empty(self):
        ns = Namespace()
        assert len(ns) == 0

    def test_init_with_dict(self):
        data = {"key1": "value1", "key2": "value2"}
        ns = Namespace(data)
        assert ns["key1"] == "value1"
        assert ns["key2"] == "value2"

    def test_init_with_kwargs(self):
        ns = Namespace(key1="value1", key2="value2")
        assert ns["key1"] == "value1"
        assert ns["key2"] == "value2"

    def test_attribute_access(self):
        ns = Namespace({"key1": "value1"})
        assert ns.key1 == "value1"

    def test_attribute_assignment(self):
        ns = Namespace()
        ns.key1 = "value1"
        assert ns["key1"] == "value1"
        assert ns.key1 == "value1"

    def test_nested_dict_conversion(self):
        data = {"level1": {"level2": {"level3": "value"}}}
        ns = Namespace(data)
        assert isinstance(ns.level1, Namespace)
        assert isinstance(ns.level1.level2, Namespace)
        assert ns.level1.level2.level3 == "value"

    def test_attribute_error(self):
        ns = Namespace()
        with pytest.raises(AttributeError):
            _ = ns.nonexistent_key
