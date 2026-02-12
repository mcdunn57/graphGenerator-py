from faker import Faker
import random
from typing import Any, Optional

class Provider:
    """
    A wrapper around Faker to generate semantic properties and domain-specific data.
    Includes deterministic generation for tax-specific fields (e.g., SSNs).
    """
    def __init__(self, seed: Optional[int] = None):
        self._faker = Faker()
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)
        
        # Reserved ranges for SSNs (Area numbers 900-999 are invalid/reserved)
        # Using 900-999 ensures we never generate a valid real-world SSN.
        self._ssn_range = range(900, 1000) 

    def name(self) -> str:
        return self._faker.name()

    def date_time(self) -> str:
        return self._faker.iso8601()

    def uuid4(self) -> str:
        return self._faker.uuid4()
    
    def random_int(self, min: int = 0, max: int = 100) -> int:
        return self._faker.random_int(min=min, max=max)

    def ssn(self) -> str:
        """
        Generate a synthetic SSN in the format XXX-XX-XXXX.
        Uses the reserved area range 900-999.
        """
        area = random.choice(self._ssn_range)
        group = random.randint(1, 99)
        serial = random.randint(1, 9999)
        return f"{area:03d}-{group:02d}-{serial:04d}"

    def unique_ssn(self) -> str:
        """
        Generate a unique, sequential SSN from the reserved range.
        Useful for deterministic testing.
        """
        if not hasattr(self, '_ssn_iterator'):
            self._ssn_iterator = (
                f"{area:03d}-{group:02d}-{serial:04d}"
                for area in self._ssn_range
                for group in range(1, 100)
                for serial in range(1, 10000)
            )
        try:
            return next(self._ssn_iterator)
        except StopIteration:
            raise StopIteration("Exhausted unique SSN range.")

    def company(self) -> str:
        return self._faker.company()
        
    def generic(self, method_name: str, *args, **kwargs) -> Any:
        """
        Delegate to Faker for any other method.
        """
        # Check if the method exists on the Provider instance itself
        if hasattr(self, method_name) and method_name != "generic":
            return getattr(self, method_name)(*args, **kwargs)

        if hasattr(self._faker, method_name):
            return getattr(self._faker, method_name)(*args, **kwargs)
        raise AttributeError(f"Provider has no attribute '{method_name}'")
