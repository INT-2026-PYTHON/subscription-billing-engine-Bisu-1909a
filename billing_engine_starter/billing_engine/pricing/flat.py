"""
FlatRate — same charge every period regardless of usage.

Example: ₹999/month subscription, no matter how much the customer uses.
"""

from billing_engine.money import Money
from billing_engine.pricing.base import PricingStrategy


class FlatRate(PricingStrategy):
    """Charges a fixed amount every billing period."""

    def __init__(self, amount: Money) -> None:
        # TODO Day 1
        if not isinstance(amount, Money):
            raise TypeError("amount must be a money instance")
        
        if amount.is_negative():
            raise ValueError("Negative value of amount not allowed")
        
        self.amount = amount

    def calculate(self, quantity: int) -> Money:
        # TODO Day 1
        return self.amount

