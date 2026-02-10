# Walkthrough - GraphGenerator-Py

## Implemented Features

### Core Architecture
- **Registry**: Thread-safe singleton for tracking generated IDs and managing state.
- **Provider**: Wrapper around Faker with deterministic SSN generation.
- **Topology**: NetworkX integration for graph structure generation.

### Declarative API
- **`@node`**: Decorator to define node metadata (label, count).
- **`@relationship`**: Decorator to define relationship logic (cardinality).
- **`Field`**: Descriptor for node properties with constraints and reference binding.
- **`ComputedField`**: Intra-node calculation logic.

### Ingestion Engine
### Ingestion Engine
- **`BatchGenerator`**: Generates batches of data from Python objects and dynamic schema definitions.
- **`CSVExporter`**: Exports generated data to CSV files in `generator_output/`.
- **`Neo4jConnector`**: (Optional) Handles connection and `UNWIND` batch ingestion.
- **`SchemaValidator`**: Pre-flight checks for schema existence.

### Reference Data Ingestor
- **`ReferenceStore`**: Manages loading and caching of CSV/JSON/Parquet files.
- **`ReferenceSource`**: API for weighted and sequential sampling.

### CSV Schema Definition (Refactoring)
- **`SchemaLoader`**: Scans a directory for CSV files (`Node_*.csv`, `Rel_*.csv`) to infer schema.
- **Dynamic Generation**: `BatchGenerator` now supports generating data directly from inferred schema.

### Validation & Verification
- **`GraphVerifier`**: Suite of checks for Path Integrity, Temporal Consistency, Cardinality, and PII Collision.

## Verification Results

### Unit Tests
The following unit tests were executed and passed:
- `tests/test_registry.py`: Verified Singleton behavior and storage.
- `tests/test_generator.py`: Verified node generation logic and computed fields.
- `tests/test_references.py`: Verified reference data binding and sampling.
- `tests/test_csv_generation.py`: Verified CSV-driven schema loading and generation.
- `tests/test_csv_export.py`: Verified CSV export of nodes and relationships.

```
tests/test_generator.py .                       [ 20%]
tests/test_references.py .                      [ 40%]
tests/test_registry.py ..                       [ 80%]
tests/test_csv_generation.py .                  [100%]
tests/test_csv_generation.py .                  [ 80%]
tests/test_csv_export.py ..                     [100%]
================== 7 passed ==================
```

### Next Steps
1. **Neo4j Integeration**: Connect to a running Neo4j instance to run the Integration Tests (using `Neo4jConnector` and `GraphVerifier`).
2. **Tax Logic Expansion**: Implement complex inter-node propagation using the groundwork laid in `TaxRules` and `BatchGenerator`.

## Usage Example (Python API)

```python
from graph_generator.api.decorators import node, relationship
from graph_generator.api.fields import Field

@node(label="Taxpayer", count=100)
class Taxpayer:
    ssn = Field(formatter="unique_ssn", unique=True)
    name = Field(formatter="name")

# Generate and Ingest
# generator = BatchGenerator(provider, registry)
# generator.generate_nodes(Taxpayer)
```

## Usage Example (CSV-Driven)

Place `Node_Person.csv` in your directory:
```csv
id,name,age
1,Alice,30
2,Bob,25
```

Run generation:
```python
loader = SchemaLoader()
loader.load_from_directory("./data")
# generator.generate_nodes(loader.nodes[0])
```
