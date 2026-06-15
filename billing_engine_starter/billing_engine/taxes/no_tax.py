"""
NoTax — for jurisdictions where you don't charge tax (or the customer is tax-exempt).
"""

from billing_engine.money import Money
from billing_engine.taxes.base import TaxCalculator, TaxContext, TaxBreakdown


class NoTax(TaxCalculator):
    def apply(self, taxable: Money, context: TaxContext) -> TaxBreakdown:
        # Return a TaxBreakdown with zero total and empty list of components
        return TaxBreakdown(
            total=Money.zero(taxable.currency),
            components=[]  # empty list, not dict
        )

