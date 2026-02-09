import pytest
from graph_generator.core.provider import Provider
from graph_generator.core.registry import Registry
from graph_generator.engine.generator import BatchGenerator
from graph_generator.api.decorators import node, relationship
from graph_generator.api.fields import Field, ComputedField

@node(label="TestNode", count=5)
class TestNode:
    id = Field(formatter="uuid4", unique=True)
    name = Field(formatter="name")
    age = Field(formatter="random_int", min=18, max=99)
    # Computed
    is_adult = ComputedField(fn=lambda n: n.age >= 18)

def test_node_generation():
    registry = Registry()
    registry.clear()
    provider = Provider(seed=42)
    generator = BatchGenerator(provider, registry)
    
    batches = list(generator.generate_nodes(TestNode, batch_size=2))
    
    assert len(batches) == 3 # 2, 2, 1
    
    all_nodes = [n for batch in batches for n in batch]
    assert len(all_nodes) == 5
    assert registry.get_count("TestNode") == 5
    
    for n in all_nodes:
        assert "id" in n
        assert "name" in n
        assert n["is_adult"] is True # Since min 18
