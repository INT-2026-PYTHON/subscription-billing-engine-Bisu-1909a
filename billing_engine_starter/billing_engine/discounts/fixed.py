"""
FixedAmountDiscount — e.g., flat ₹500 off.

CAPPING RULE: if the fixed amount exceeds the subtotal, return subtotal
(so the discounted total never goes below zero).
"""

from billing_engine.money import Money
from billing_engine.discounts.base import Discount, DiscountContext


class FixedAmountDiscount(Discount):
    def __init__(self, amount: Money) -> None:
        # TODO Day 1
        # Validate that amount is a Money instance
        if not isinstance(amount, Money):
            raise TypeError("amount must be a Money instance")
        # Validate that amount is not negative
        if amount.is_negative():
            raise ValueError("amount cannot be negative")
        # Store the amount
        self.amount = amount

    def apply(self, subtotal: Money, context: DiscountContext) -> Money:
        # TODO Day 1
        # Ensure same currency
        if subtotal.currency != self.amount.currency:
            raise ValueError("currency mismatch between subtotal and discount")
        # Return the smaller of subtotal or discount amount
        return min(self.amount, subtotal)

