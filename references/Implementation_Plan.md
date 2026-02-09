# Implementation Plan - GraphGenerator-Py

## Goal Description
Develop the GraphGenerator-Py library, a declarative, schema-driven synthesis engine for creating structurally plausible and semantically rich graph data for Neo4j, optimized for the IRS tax domain. The library will support advanced features like "Graph-Schema-as-Code", conditional cardinality, calculated fields, and hybrid generation using reference data.

## User Review Required
> [!IMPORTANT]
> **Mock Neo4j Instance**: Access to a Mock Neo4j Bolt instance or a local container is assumed to be available **after** the code base development for final verification, allowing for offline development of the core logic.

> [!NOTE]
> **Data Privacy**: The "Provider Layer" will be configured to generate *synthetic* PII (e.g., SSNs in reserved ranges) to strictly avoid real-world collisions. This is a critical safety feature.

## Proposed Changes

### Project Initialization
#### [NEW] [pyproject.toml](file:///Users/mike/Documents/python_stuff/graphGenerator-py/pyproject.toml)
- Define project metadata and dependencies: `neo4j`, `faker`, `networkx`, `pandas`.

#### [NEW] [README.md](file:///Users/mike/Documents/python_stuff/graphGenerator-py/README.md)
- Project overview and usage instructions.

### Core Architecture
#### [NEW] [src/core/registry.py](file:///Users/mike/Documents/python_stuff/graphGenerator-py/src/core/registry.py)
- **Registry Module**: A thread-safe singleton to track generated IDs for node labels. Supports in-memory storage with potential for disk-overflow (using SQLite or similar) for large volumes.

#### [NEW] [src/core/provider.py](file:///Users/mike/Documents/python_stuff/graphGenerator-py/src/core/provider.py)
- **Provider Layer**: Wrapper around `faker` to generate domain-specific data (names, dates, tax forms). Includes deterministic generation for SSNs/TINs using reserved ranges.

#### [NEW] [src/core/topology.py](file:///Users/mike/Documents/python_stuff/graphGenerator-py/src/core/topology.py)
- **Topology Engine**: Integration with `networkx` to support graph generation models (e.g., Watts-Strogatz) ensuring structural fidelity.

### Declarative API
#### [NEW] [src/api/decorators.py](file:///Users/mike/Documents/python_stuff/graphGenerator-py/src/api/decorators.py)
- **`@node`**: Class decorator to define node metadata (label, count).
- **`@relationship`**: Class decorator to define relationship types and source/target nodes.

#### [NEW] [src/api/fields.py](file:///Users/mike/Documents/python_stuff/graphGenerator-py/src/api/fields.py)
- **`Field`**: Descriptor for defining node properties with formatters and constraints.
- **`ComputedField`**: For intra-node calculations (e.g., `total = A + B`).

### Ingestion Engine
#### [NEW] [src/engine/generator.py](file:///Users/mike/Documents/python_stuff/graphGenerator-py/src/engine/generator.py)
- **BatchGenerator**: Logic to convert Python objects into batched JSON/Dictionary structures.
- **Ingestion Pipeline**: Handles the `UNWIND` strategy for efficient bulk loading into Neo4j.

#### [NEW] [src/engine/validator.py](file:///Users/mike/Documents/python_stuff/graphGenerator-py/src/engine/validator.py)
- **Pre-flight Check**: Queries Neo4j schema to validate labels/relationships exist *before* generation.

### Tax Domain Extensions
#### [NEW] [src/domain/tax_rules.py](file:///Users/mike/Documents/python_stuff/graphGenerator-py/src/domain/tax_rules.py)
- **Conditional Cardinality**: Logic for "if-then" relationship counts (e.g., strict 1:1 for Spouses if "Married Filing Jointly").
- **Inter-node Propagation**: "Push" logic for consistency across related forms.

### Reference Data Ingestor
#### [NEW] [src/ingestor/reference.py](file:///Users/mike/Documents/python_stuff/graphGenerator-py/src/ingestor/reference.py)
- **ReferenceStore**: Manages loading and caching of external files (CSV, JSON, Parquet).
- **ReferenceSource**: API to bind fields to reference data columns with sampling strategies (Weighted, Sequential, Categorical).

## Verification Plan

### Automated Tests
- **Unit Tests**: Test individual components (Registry, Provider, Field validation).
- **Integration Tests**:
    - **Graph Health Check**: Verify generated graph structure and connectivity.
    - **Path Integrity**: Validate lineage between critical nodes.
    - **Temporal Consistency**: Ensure relationship timestamps make sense relative to node creation.
    - **Reference Coverage**: Confirm input files are utilized as expected.

### Manual Verification
- **Mock Audit**: Run queries to verify tax compliance logic (e.g., Sum of parts equals total).
- **PII Check**: Scan generated data for accidental real-world PII collisions.
