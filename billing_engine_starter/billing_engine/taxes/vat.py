"""
VATCalculator — single-rate VAT (e.g. 19% in Germany).
"""

from decimal import Decimal

from billing_engine.money import Money
from billing_engine.taxes.base import TaxCalculator, TaxContext, TaxBreakdown


class VATCalculator(TaxCalculator):
    def __init__(self, rate: Decimal) -> None:
        #   - Validate 0 <= rate <= 1.
        #   - Reject float.
        #   - Store on self.
        def __init__(self, rate: Decimal) -> None:
         if isinstance(rate, float):
            raise TypeError("value must be a decimal not float")
       
        if not isinstance(rate, Decimal):
            raise TypeError("value must be a decimal")
      
        if rate < Decimal("0") or rate > Decimal("1"):
            raise ValueError("value between 0 and 1")
        
        self.rate = rate

    def apply(self, taxable: Money, context: TaxContext) -> TaxBreakdown:
        #   - vat = taxable * self.rate
        #   - Return TaxBreakdown with one component (f"VAT {percent}%", vat) and total = vat.
        #   - Tip: format the rate as a percentage cleanly.
        # Compute VAT amount
        vat_amount = taxable * self.rate
        percent = (self.rate * 100).quantize(Decimal("1"))
        label = f"VAT {percent}%"
        
        return TaxBreakdown(
            total=vat_amount,
            components={label: vat_amount}
        )
