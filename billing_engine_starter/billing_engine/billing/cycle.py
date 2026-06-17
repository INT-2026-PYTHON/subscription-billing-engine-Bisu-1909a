"""
BillingCycle — finds due subscriptions, generates invoices, posts ledger DEBITs,
advances the subscription period. Must be IDEMPOTENT (safe to run twice).
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date
from typing import Callable, Optional

from billing_engine.db import (
    Database,
    CustomerRepository,
    PlanRepository,
    SubscriptionRepository,
    UsageRecordRepository,
    InvoiceRepository,
    InvoiceLineItemRepository,
    LedgerRepository,
)
from billing_engine.models import (
    Subscription,
    SubscriptionStatus,
    InvoiceStatus,
    LedgerDirection,
    LedgerEntry,
)
from billing_engine.billing.pipeline import build_invoice


@dataclass
class BillingResult:
    invoices_created: int
    invoices_skipped_duplicate: int
    trials_activated: int


class BillingCycle:
    """Day-3 deliverable. Day-4 stretch: add `upgrade_subscription(...)`."""

    def __init__(
        self,
        db: Database,
        customer_repo: CustomerRepository,
        plan_repo: PlanRepository,
        subscription_repo: SubscriptionRepository,
        usage_repo: UsageRecordRepository,
        invoice_repo: InvoiceRepository,
        line_item_repo: InvoiceLineItemRepository,
        ledger_repo: LedgerRepository,
        strategy_factory: Callable,    # given a Plan, returns a PricingStrategy
        discount_factory: Callable,    # given a discount_id or None, returns a Discount or None
        tax_factory: Callable,         # given a Customer, returns (TaxCalculator, TaxContext)
    ) -> None:
        self.db = db
        self.customer_repo = customer_repo
        self.plan_repo = plan_repo
        self.subscription_repo = subscription_repo
        self.usage_repo = usage_repo
        self.invoice_repo = invoice_repo
        self.line_item_repo = line_item_repo
        self.ledger_repo = ledger_repo
        self.strategy_factory = strategy_factory
        self.discount_factory = discount_factory
        self.tax_factory = tax_factory

    def run(self, as_of: date) -> BillingResult:
        """Bill all subscriptions whose current period ends on or before `as_of`."""
        invoices_created = 0
        invoices_skipped = 0
        trials_activated = 0

        # Phase 1: Promote ended trials to ACTIVE
        for sub in self.subscription_repo.list_all():
            if (
                sub.status == SubscriptionStatus.TRIAL
                and sub.trial_end is not None
                and sub.trial_end <= as_of
            ):
                self.subscription_repo.update_status(sub.id, SubscriptionStatus.ACTIVE)
                trials_activated += 1

        # Phase 2: Bill due subscriptions
        due_subs = self.subscription_repo.get_due_for_billing(as_of)

        for sub in due_subs:
            plan = self.plan_repo.get(sub.plan_id)
            customer = self.customer_repo.get(sub.customer_id)

            strategy = self.strategy_factory(plan)
            discount = self.discount_factory(sub.discount_id)
            tax_calc, tax_context = self.tax_factory(customer)

            usage_quantity = self.usage_repo.sum_for_period(
                sub.id, "units", sub.current_period_start, sub.current_period_end
            )

            invoice_count_so_far = self.invoice_repo.count_for_subscription(sub.id)

            draft = build_invoice(
                subscription=sub,
                plan=plan,
                strategy=strategy,
                discount=discount,
                tax_calc=tax_calc,
                tax_context=tax_context,
                usage_quantity=usage_quantity,
                period_start=sub.current_period_start,
                period_end=sub.current_period_end,
                invoice_count_so_far=invoice_count_so_far,
            )

            # Everything must be atomic
            try:
                with self.db.transaction() as conn:
                    # 1. Save invoice
                    saved_invoice = self.invoice_repo.add(draft, conn=conn)

                    # 2. Save line items
                    for li in getattr(draft, 'line_items', []):   # safe access
                        li.invoice_id = saved_invoice.id
                        self.line_item_repo.add(li, conn=conn)

                    # 3. Post ledger DEBIT
                    self.ledger_repo.add(
                        LedgerEntry(
                            id=None,
                            customer_id=sub.customer_id,
                            invoice_id=saved_invoice.id,
                            direction=LedgerDirection.DEBIT,
                            amount=saved_invoice.total,
                            reason=f"Invoice #{saved_invoice.id} for subscription {sub.id}",
                        ),
                        conn=conn
                    )

                    # 4. Advance period
                    next_start = sub.current_period_end
                    next_end = self._calculate_next_period_end(sub, next_start)
                    self.subscription_repo.update_period(
                        sub.id, next_start, next_end, conn=conn
                    )

                    invoices_created += 1

            except sqlite3.IntegrityError:
                invoices_skipped += 1

        return BillingResult(invoices_created, invoices_skipped, trials_activated)

    def _calculate_next_period_end(self, sub: Subscription, new_start: date) -> date:
        """Calculate next billing period end (currently monthly only)."""
        # For simplicity - extend later for yearly, quarterly, etc.
        from dateutil.relativedelta import relativedelta
        return new_start + relativedelta(months=1)

    def upgrade_subscription(self, subscription_id: int, new_plan_id: int, switch_date: date) -> None:
        """Mid-cycle upgrade — Day 4 stretch."""
        raise NotImplementedError("Day 4: implement BillingCycle.upgrade_subscription")