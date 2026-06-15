import os
import sys
from decimal import Decimal

# Get the directory of demo.py, then go up one level to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)

# Now your imports will work perfectly
from billing_engine.money import Money

# Corrected imports matching your exact billing_engine_starter folder structure
from billing_engine_starter.billing_engine.money import Money
from billing_engine_starter.billing_engine.pricing import FlatRate, TieredPricing, Tier
from billing_engine_starter.billing_engine.discounts import PercentageDiscount, DiscountContext
from billing_engine_starter.billing_engine.taxes import GSTCalculator, TaxContext

def main():
    # 1. Flat plan calculation
    flat = FlatRate(Money("999", "INR"))
    print("Flat Plan Subtotal:", flat.calculate(0))  # Output: INR 999.00

    # 2. Tiered pricing calculation
    tiers = TieredPricing([
        Tier(0, 1000, Money("2.00", "INR")),
        Tier(1000, None, Money("1.50", "INR")),
    ])
    print("Tiered Pricing Subtotal:", tiers.calculate(2000))  # Output: INR 3500.00

    # 3. Discount + tax calculation
    base = flat.calculate(0)
    disc = PercentageDiscount(Decimal("0.50")).apply(base, DiscountContext(0))
    taxable = base - disc
    
    # GST setup (9% CGST, 9% SGST, 18% IGST)
    gst = GSTCalculator(Decimal("0.09"), Decimal("0.09"), Decimal("0.18"))
    ctx = TaxContext("IN", "MH", "MH")  # Intra-state transaction (MH to MH)
    
    # Displays the absolute final total (Taxable amount + applied GST)
    print("Grand Total with GST:", gst.apply(taxable, ctx).total)

if __name__ == "__main__":
    main()
