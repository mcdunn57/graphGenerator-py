import pytest
import pandas as pd
import os
from graph_generator.ingestor.reference import ReferenceStore
from graph_generator.engine.generator import BatchGenerator
from graph_generator.core.provider import Provider
from graph_generator.core.registry import Registry
from graph_generator.api.decorators import node
from graph_generator.api.fields import Field

def test_reference_binding(tmp_path):
    # Create dummy csv
    csv_path = tmp_path / "test.csv"
    df = pd.DataFrame({"col1": ["A", "B", "C"], "Weight": [1, 1, 1]})
    df.to_csv(csv_path, index=False)
    
    store = ReferenceStore()
    # The generator will access the store singleton
    
    @node(label="RefNode", count=3)
    class RefNode:
        val = Field(source=str(csv_path), column="col1", strategy="sequential")
        
    registry = Registry()
    registry.clear()
    provider = Provider()
    generator = BatchGenerator(provider, registry)
    
    batches = list(generator.generate_nodes(RefNode))
    nodes = [n for batch in batches for n in batch]
    
    vals = [n["val"] for n in nodes]
    assert sorted(vals) == ["A", "B", "C"]
