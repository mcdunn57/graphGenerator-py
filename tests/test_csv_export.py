
import pytest
import os
import csv
from graph_generator.engine.exporter import CSVExporter

def test_csv_export_nodes(tmp_path):
    exporter = CSVExporter(output_dir=str(tmp_path))
    
    batch = [
        {"id": 1, "name": "Alice", "_internal": "ignored"},
        {"id": 2, "name": "Bob", "_internal": "ignored"}
    ]
    
    exporter.export_nodes("Person", batch)
    
    expected_file = tmp_path / "Node_Person.csv"
    assert expected_file.exists()
    
    with open(expected_file, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["name"] == "Alice"
        assert rows[1]["name"] == "Bob"
        assert "_internal" not in rows[0]

def test_csv_export_relationships(tmp_path):
    exporter = CSVExporter(output_dir=str(tmp_path))
    
    batch = [
        {"_source_id": 1, "_target_id": 10, "since": 2020},
        {"_source_id": 2, "_target_id": 20, "since": 2021}
    ]
    
    exporter.export_relationships("KNOWS", "Person", "Company", batch)
    
    expected_file = tmp_path / "Rel_KNOWS_Person_Company.csv"
    assert expected_file.exists()
    
    with open(expected_file, "r") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        assert ":START_ID" in fields
        assert ":END_ID" in fields
        assert "since" in fields
        
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0][":START_ID"] == "1"
        assert rows[0][":END_ID"] == "10"
