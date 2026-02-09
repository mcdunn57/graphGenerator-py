from typing import Any

class TaxRules:
    """
    Helpers for tax domain specific logic and calculations.
    """
    
    @staticmethod
    def calculate_total_income(wages: float, interest: float, dividends: float) -> float:
        return wages + interest + dividends

    @staticmethod
    def is_mfj(filing_status: str) -> bool:
        return filing_status == "MFJ"

    @staticmethod
    def calculate_tax(income: float) -> float:
        # Simplified placeholder logic
        if income < 10000:
            return 0
        elif income < 50000:
            return income * 0.15
        else:
            return income * 0.25
