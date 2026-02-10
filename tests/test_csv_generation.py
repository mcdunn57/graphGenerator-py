import pytest
import os
import csv
from graph_generator.schema.loader import SchemaLoader
from graph_generator.engine.generator import BatchGenerator
from graph_generator.core.provider import Provider
from graph_generator.core.registry import Registry

def test_csv_schema_loading_and_generation(tmp_path):
    # 1. Create dummy CSVs
    node_file = tmp_path / "Node_Person.csv"
    with open(node_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "age"])
        writer.writerow(["1", "Alice", "30"])
        writer.writerow(["2", "Bob", "25"])
        
    rel_file = tmp_path / "Rel_KNOWS_Person_Person.csv"
    with open(rel_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["since", "strength"])
        writer.writerow(["2020", "high"])

    # 2. Load Schema
    loader = SchemaLoader()
    loader.load_from_directory(str(tmp_path))
    
    assert len(loader.nodes) == 1
    assert loader.nodes[0].label == "Person"
    assert loader.nodes[0].count == 2
    
    assert len(loader.relationships) == 1
    assert loader.relationships[0].type == "KNOWS"
    
    # 3. Generate Data
    registry = Registry()
    provider = Provider()
    generator = BatchGenerator(provider, registry)
    
    # Generate Nodes
    node_batches = list(generator.generate_nodes(loader.nodes[0]))
    assert len(node_batches) > 0
    nodes = [n for batch in node_batches for n in batch]
    assert len(nodes) == 2
    assert nodes[0]['name'] == 'Alice' # Sequential sampling should match row order
    assert nodes[1]['name'] == 'Bob'
    
    # Check Registry
    ids = registry.get_all("Person")
    assert len(ids) == 0 # No unique field defined in CSV yet (unless we specify it)
    
    # To test relationships, we need IDs in registry. 
    # Let's manually register them for this test since we didn't define unique constraints in CSV loader yet.
    # The current SchemaLoader uses 'Field(..., strategy="sequential")' but doesn't set unique=True.
    registry.register("Person", "1")
    registry.register("Person", "2")
    
    # Generate Relationships
    # Note: Rel_KNOWS_Person_Person.csv implies structure but our loader is naive.
    # It extracted from_node="Person", to_node="Person" from filename.
    
    rel_batches = list(generator.generate_relationships(loader.relationships[0]))
    assert len(rel_batches) > 0
    rels = [r for batch in rel_batches for r in batch]
    
    # Cardinality defaults to 1-3 random if not specified.
    # Since we have 2 Person nodes, it should generate some relationships.
    assert len(rels) > 0
    assert 'strength' in rels[0]
