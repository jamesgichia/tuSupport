from django.db import models
from core.models import TenantScopedModel
from django.conf import settings

class Fundraiser(TenantScopedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        CLOSED = "closed", "Closed"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.organization})"


class Contribution(TenantScopedModel):
    """
    Records a single contribution to a fundraiser.
    Inherits organization FK + TenantManager from TenantScopedModel —
    tenant isolation is automatic, not manual.
    """
    class PaymentMethod(models.TextChoices):
        MPESA = 'mpesa', 'M-Pesa'
        MANUAL = 'manual', 'Manual'

    fundraiser = models.ForeignKey(
        Fundraiser,
        on_delete=models.PROTECT,   # PROTECT not CASCADE — never silently delete money records
        related_name='contributions'
    )
    contributor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,   # same reason — audit trail must survive user deletion
        related_name='contributions'
    )
    contributor_name = models.CharField(
				max_length=100,
				blank=True,
				null=True,
				help_text="Name of contributor if not a registered platform user."
		)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.MANUAL
    )
    # Phone number for M-Pesa reconciliation — nullable for manual payments
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    # External transaction ID from M-Pesa — blank until payment confirmed
    transaction_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.contributor} → {self.fundraiser} ({self.amount})"
