# GraphGenerator-Py

GraphGenerator-Py is a declarative, schema-driven synthesis engine for creating structurally plausible and semantically rich graph data for Neo4j. It is designed to go beyond simple random generation by enforcing mathematical dependencies, regulatory logic (specifically for the IRS tax domain), and topological fidelity.

## Features

- **Declarative Schema Definition**: Define nodes and relationships using Python classes and decorators (`@node`, `@relationship`).
- **Domain-Aware Generation**: Generate data that adheres to complex business rules and functional dependencies (e.g., calculated tax fields).
- **Graph Topology Models**: Integration with NetworkX to generate realistic graph structures (Watts-Strogatz, etc.).
- **Hybrid Generation**: Ingest and augment existing reference data (CSV, Parquet) with weighted or sequential sampling.
- **Neo4j Optimization**: Optimized `UNWIND` batch ingestion strategy.
- **Data-First Schema**: Auto-generate schema and data directly from CSV files (`Node_*.csv`, `Rel_*.csv`).

## Installation

```bash
pip install .
```

## Usage

### 1. Data-First Generation (Recommended)
The simplest way to use GraphGenerator-Py is to provide CSV files defining your nodes and relationships. The library will read them, generate synthetic data, and output new CSV files.

1. Create a directory (e.g., `./data`) and add your input files:
   - `Node_<Label>.csv`: Headers define properties.
   - `Rel_<Type>.csv`: Headers define properties.

   **Example `Node_Person.csv`**:
   ```csv
   id,name,age
   1,Alice,30
   2,Bob,25
   ```

2. Run the Generator:

   ```python
   from graph_generator.schema.loader import SchemaLoader
   from graph_generator.core.registry import Registry
   from graph_generator.core.provider import Provider
   from graph_generator.engine.generator import BatchGenerator
   from graph_generator.engine.exporter import CSVExporter

   # 1. Initialize Components
   loader = SchemaLoader()
   loader.load_from_directory("./data")
   
   registry = Registry()
   provider = Provider()
   generator = BatchGenerator(provider, registry)
   exporter = CSVExporter(output_dir="./generator_output")

   # 2. Generate and Export Nodes
   for node_def in loader.nodes:
       print(f"Processing Node: {node_def.label}")
       for batch in generator.generate_nodes(node_def):
           exporter.export_nodes(node_def.label, batch)

   # 3. Generate and Export Relationships
   for rel_def in loader.relationships:
       print(f"Processing Relationship: {rel_def.type}")
       for batch in generator.generate_relationships(rel_def):
            # Note: The loader infers from_node/to_node from filename if possible 
            # or uses generic handling. Ensure filenames like Rel_TYPE_FROM_TO.csv for best results.
            exporter.export_relationships(rel_def.type, rel_def.from_node, rel_def.to_node, batch)
   
   print("Generation Complete! Check ./generator_output")
   ```

### 2. Code-First Generation (Advanced)
For more complex logic (calculated fields, conditional probabilities), define your schema using Python classes.

1. Define Schema:
   ```python
   from graph_generator.api.decorators import node, relationship
   from graph_generator.api.fields import Field, ComputedField

   @node(label="Taxpayer", count=100)
   class Taxpayer:
       ssn = Field(formatter="unique_ssn", unique=True)
       name = Field(formatter="name")
       wages = Field(formatter="random_int", min=30000, max=150000)
       
   @node(label="Form1040", count=100)
   class Form1040:
       filing_year = Field(formatter="random_int", min=2020, max=2024)

   @relationship(type="FILED_BY", from_node="Form1040", to_node="Taxpayer")
   class FiledByRel:
       date = Field(formatter="date_time")
   ```

2. Generate and Export:
   ```python
   # ... Initialize generator and exporter as above ...

   for batch in generator.generate_nodes(Taxpayer):
       exporter.export_nodes("Taxpayer", batch)
       
   for batch in generator.generate_relationships(FiledByRel):
       exporter.export_relationships("FILED_BY", "Form1040", "Taxpayer", batch)
   ```

### 3. Optional: Direct Neo4j Ingestion
You can ingest data directly into Neo4j using the `Neo4jConnector` if preferred.

```python
from graph_generator.engine.connector import Neo4jConnector

connector = Neo4jConnector("bolt://localhost:7687", ("neo4j", "password"))
try:
    for batch in generator.generate_nodes(Taxpayer):
        connector.ingest_nodes("Taxpayer", batch)
finally:
    connector.close()
```

## Development

1. Install dependencies:
   ```bash
   pip install -e .
   ```
2. Run tests:
   ```bash
   pytest
   ```


### What you need to do:
To "activate" this file and install your project along with its dependencies, run the following command in your terminal from the root directory:

bash
pip install -e .
-e (editable): This flag is important for development. It means any changes you make to the code in src/ will be immediately reflected without needing to reinstall.
.: Tells pip to look for the 
pyproject.toml
 in the current directory.
Once you run this, you will be able to import your library (import graph_generator) from anywhere in your environment.
'''