import threading
from collections import defaultdict
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class Registry:
    """
    A thread-safe singleton registry to track generated IDs and manage state 
    across the generation process.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Registry, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self._store: Dict[str, List[Any]] = defaultdict(list)
        self._data_lock = threading.Lock()
        logger.info("Registry initialized.")

    def register(self, label: str, value: Any):
        """
        Register a value (e.g., ID) for a specific label.
        """
        with self._data_lock:
            self._store[label].append(value)

    def get_all(self, label: str) -> List[Any]:
        """
        Retrieve all registered values for a label.
        """
        with self._data_lock:
            return list(self._store.get(label, []))

    def get_count(self, label: str) -> int:
        """
        Get the count of registered items for a label.
        """
        with self._data_lock:
            return len(self._store.get(label, []))

    def clear(self):
        """
        Clear the registry.
        """
        with self._data_lock:
            self._store.clear()
        logger.info("Registry cleared.")
