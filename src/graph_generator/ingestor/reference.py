import pandas as pd
import random
from typing import Any, List, Optional
import os
import logging

logger = logging.getLogger(__name__)

class ReferenceSource:
    """
    Represents a source of reference data (CSV, JSON, Parquet).
    Supports sequential and weighted sampling.
    """
    def __init__(self, path: str, sampling: str = "weighted", key_column: str = None):
        self.path = path
        self.sampling = sampling
        self.key_column = key_column
        self.data = pd.DataFrame()
        self._loaded = False
        self._seq_index = 0

    def load(self):
        if self._loaded:
            return
        
        if not os.path.exists(self.path):
             # Try looking in 'references' dir relative to project root?
             # For now assume absolute or correct relative path.
             pass

        ext = os.path.splitext(self.path)[1].lower()
        try:
            if ext == '.csv':
                self.data = pd.read_csv(self.path)
            elif ext == '.json':
                self.data = pd.read_json(self.path)
            elif ext == '.parquet':
                self.data = pd.read_parquet(self.path)
            else:
                raise ValueError(f"Unsupported file format: {ext}")
            self._loaded = True
            logger.info(f"Loaded reference data from {self.path}: {len(self.data)} rows.")
        except Exception as e:
            logger.error(f"Failed to load reference data from {self.path}: {e}")
            raise

    def sample(self, column: str, count: int = 1) -> List[Any]:
        """
        Sample values from the specified column.
        """
        if not self._loaded:
            self.load()
            
        if column not in self.data.columns:
            # If column is None and data has 1 column, use it?
            raise ValueError(f"Column '{column}' not found in {self.path}. Available: {list(self.data.columns)}")

        if self.sampling == "sequential":
            # Return next 'count' items
            start = self._seq_index
            end = start + count
            
            if end > len(self.data):
                 raise ValueError(f"Exhausted reference data in {self.path} for sequential sampling. Needed {end}, available {len(self.data)}.")
            
            result = self.data.iloc[start:end][column].tolist()
            self._seq_index = end
            return result
            
        elif self.sampling == "weighted":
            # Check for 'Weight' column
            if "Weight" in self.data.columns:
                return self.data.sample(n=count, weights="Weight", replace=True)[column].tolist()
            else:
                return self.data.sample(n=count, replace=True)[column].tolist()
        
        else:
            # Default random
            return self.data.sample(n=count, replace=True)[column].tolist()

class ReferenceStore:
    """
    Singleton manager for ReferenceSources.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ReferenceStore, cls).__new__(cls)
            cls._instance.sources = {}
        return cls._instance
    
    def get_source(self, path: str, **kwargs) -> ReferenceSource:
        if path not in self.sources:
            self.sources[path] = ReferenceSource(path, **kwargs)
        return self.sources[path]
