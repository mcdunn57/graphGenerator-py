# Refactoring Plan - CSV-Based Schema Definition

## Goal Description
Refactor the library to support defining the graph schema (nodes and relationships) and populating data directly from input CSV files. This enables a "Data-First" approach where users provide sample files instead of writing Python code.

## Current State Analysis
- **Current Integration**: The library uses Python classes decorated with `@node` and `@relationship` to define schema.
- **Reference Data**: CSV files are only used as *sources* for specific fields via `ReferenceSource`, not as definitions of the schema itself.
- **Gap**: There is no mechanism to auto-generate node/relationship definitions from file headers or content.

## Proposed Changes

### 1. Schema Definition Module
#### [NEW] [src/graph_generator/schema/loader.py](file:///Users/mike/Documents/python_stuff/graphGenerator-py/src/graph_generator/schema/loader.py)
- **`SchemaLoader`**: Scans a directory for CSV files to infer schema.
    - **Node Files**: `Node_<Label>.csv` (or just `<Label>.csv` if configured).
    - **Relationship Files**: `Rel_<Type>.csv` (or `<Type>.csv`).
- **`SchemaDefinition`**: data class to hold the inferred schema (Node definitions, Relationship definitions).

### 2. Dynamic Definition Generation
#### [MODIFY] [src/graph_generator/engine/generator.py](file:///Users/mike/Documents/python_stuff/graphGenerator-py/src/graph_generator/engine/generator.py)
- **`generate_from_schema(schema_def)`**: A new method in `BatchGenerator` that iterates over the definitions provided by `SchemaLoader`.
- **Dynamic Classes**:
    - Instead of requiring a decorated class, the generator will accept `NodeDefinition` objects (created by the loader) that contain:
        - `label`: Derived from filename.
        - `fields`: Derived from CSV headers.
        - `data_source`: The CSV file itself (implicitly a `ReferenceSource` with `sequential` sampling).

### 3. Updated Ingestion Pipeline
#### [MODIFY] [src/graph_generator/engine/connector.py](file:///Users/mike/Documents/python_stuff/graphGenerator-py/src/graph_generator/engine/connector.py)
- Ensure `ingest_nodes` and `ingest_relationships` can handle dynamic dictionaries without relying on strict class attributes if they don't exist.

## Verification Plan

### Automated Tests
- **`tests/test_schema_loader.py`**:
    - Verify schema inference from sample CSVs.
    - Verify correct identification of node labels and relationship types.
- **`tests/test_csv_generation.py`**:
    - Verify data generated matches input CSV content (sequential/strict mode).

### Manual Verification
- Create sample `Taxpayer.csv` and `FiledBy.csv`.
- Run the new `SchemaLoader` and ingestion process.
- Verify data in Neo4j (Mock or Real).
