# GraphGenerator-Py

GraphGenerator-Py is a declarative, schema-driven synthesis engine for creating structurally plausible and semantically rich graph data for Neo4j. It is designed to go beyond simple random generation by enforcing mathematical dependencies, regulatory logic (specifically for the IRS tax domain), and topological fidelity.

## Features

- **Declarative Schema Definition**: Define nodes and relationships using Python classes and decorators (`@node`, `@relationship`).
- **Domain-Aware Generation**: Generate data that adheres to complex business rules and functional dependencies (e.g., calculated tax fields).
- **Graph Topology Models**: Integration with NetworkX to generate realistic graph structures (Watts-Strogatz, etc.).
- **Hybrid Generation**: Ingest and augment existing reference data (CSV, Parquet) with weighted or sequential sampling.
- **Neo4j Optimization**: Optimized `UNWIND` batch ingestion strategy.

## Installation

```bash
pip install .
```

## Usage

(Coming soon)

## Development

1. Install dependencies:
   ```bash
   pip install -e .
   ```
2. Run tests:
   ```bash
   pytest
   ```
