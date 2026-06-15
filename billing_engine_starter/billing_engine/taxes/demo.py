from decimal import Decimal
from billing_engine.money import Money
from billing_engine.pricing import FlatRate, UsageBased, Freemium
from billing_engine.discounts import PercentageDiscount, DiscountContext
from billing_engine.taxes import GSTCalculator, TaxContext

def run_demo():
    # --- Pricing strategies ---
    flat = FlatRate(Money("1000", "INR"))
    usage = UsageBased(Money("50", "INR"))
    freemium = Freemium(free_quota=5, overage_strategy=usage)

    print("FlatRate(1):", flat.calculate(1))
    print("UsageBased(10):", usage.calculate(10))
    print("Freemium(3):", freemium.calculate(3))
    print("Freemium(8):", freemium.calculate(8))

    # --- Discounts ---
    subtotal = Money("1000", "INR")
    discount = PercentageDiscount(Decimal("0.10"))
    context = DiscountContext(invoice_count_so_far=1)
    print("Discount:", discount.apply(subtotal, context))

    # --- Taxes ---
    taxable = Money("1000", "INR")
    gst = GSTCalculator(Decimal("0.09"), Decimal("0.09"), Decimal("0.18"))
    tax_intra = TaxContext(customer_state="OD", seller_state="OD")
    tax_inter = TaxContext(customer_state="MH", seller_state="OD")

    print("GST Intra:", gst.apply(taxable, tax_intra))
    print("GST Inter:", gst.apply(taxable, tax_inter))

if __name__ == "__main__":
    run_demo()
