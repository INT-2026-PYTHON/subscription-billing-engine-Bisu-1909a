from datetime import date
from typing import Optional

from billing_engine.models import (
    Invoice, InvoiceStatus, InvoiceLineItem, LineItemKind
)
from billing_engine.money import Money
# ... other imports (DiscountContext, etc.)

def build_invoice(
    subscription: "Subscription",
    plan: "Plan",
    strategy: "PricingStrategy",
    discount: Optional["Discount"],
    tax_calc: "TaxCalculator",
    tax_context: "TaxContext",
    usage_quantity: int,
    period_start: date,
    period_end: date,
    invoice_count_so_far: int,
) -> Invoice:
    """Pure function. Returns an Invoice (id=None, status=DRAFT) ready to be persisted."""

    base = strategy.calculate(usage_quantity)

    if discount is None:
        discount_amount = Money.zero(base.currency)
    else:
        from billing_engine.discounts import DiscountContext
        context = DiscountContext(invoice_count_so_far)
        discount_amount = discount.apply(base, context)

    taxable = base - discount_amount

    breakdown = tax_calc.apply(taxable, tax_context)

    total = taxable + breakdown.total

    # Build line items (will be saved separately)
    line_items = [
        InvoiceLineItem(
            id=None,
            invoice_id=None,
            description=f"{plan.name} ({period_start} to {period_end})",
            amount=base,
            kind=LineItemKind.BASE,
        )
    ]

    if discount_amount > Money.zero(base.currency):
        line_items.append(
            InvoiceLineItem(
                id=None,
                invoice_id=None,
                description="Discount",
                amount=-discount_amount,
                kind=LineItemKind.DISCOUNT,
            )
        )

    for component in breakdown.components:
        line_items.append(
            InvoiceLineItem(
                id=None,
                invoice_id=None,
                description=component,
                amount=breakdown.total,   # usually tax amount
                kind=LineItemKind.TAX,
            )
        )

        return Invoice(
        id=None,
        subscription_id=subscription.id,
        period_start=period_start,
        period_end=period_end,
        subtotal=base,
        discount_total=discount_amount,
        tax_total=breakdown.total,
        total=total,
        status=InvoiceStatus.DRAFT,
        issued_at=None,
        pdf_path=None,
        line_items=line_items,         
    )