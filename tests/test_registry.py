import pytest
from graph_generator.core.registry import Registry

def test_registry_singleton():
    r1 = Registry()
    r2 = Registry()
    assert r1 is r2

def test_registry_storage():
    r = Registry()
    r.clear()
    r.register("User", 1)
    r.register("User", 2)
    assert r.get_count("User") == 2
    assert r.get_all("User") == [1, 2]
