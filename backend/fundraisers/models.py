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
        constraints = [
            models.CheckConstraint(
                check=(
                    ~models.Q(contributor__isnull=True) |
                    ~models.Q(contributor_name__isnull=True)
                ),
                name='contribution_has_identity'
            )
        ]

    def __str__(self):
        return f"{self.contributor} → {self.fundraiser} ({self.amount})"



class Beneficiary(TenantScopedModel):
    """
    Represents a welfare case or individual supported by the organization.
    Scoped to organization — not tied to a single fundraiser.
    The Fundraiser <-> Beneficiary link is a Phase 2 addition (M2M junction table).
    """

    class Category(models.TextChoices):
        MEDICAL = 'medical', 'Medical'
        EDUCATION = 'education', 'Education'
        FUNERAL = 'funeral', 'Funeral/Bereavement'
        DISASTER = 'disaster', 'Disaster Relief'
        OTHER = 'other', 'Other'

    class VerificationStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        VERIFIED = 'verified', 'Verified'
        ARCHIVED = 'archived', 'Archived'

    # Public-facing fields
    display_name = models.CharField(
        max_length=200,
        help_text="Public label e.g. 'The Omondi Family' or 'Baby Jane Medical Fund'"
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER
    )
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )

    # Private/admin fields
    full_name = models.CharField(max_length=200)
    national_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="National ID or passport — for payout verification and fraud prevention"
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    relationship_to_org = models.CharField(max_length=100, blank=True, null=True)
    internal_notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
						models.UniqueConstraint(
								fields=['organization', 'national_id'],
								condition=models.Q(national_id__isnull=False),
								name='unique_national_id_per_org'
						)
				]

    def __str__(self):
        return f"{self.display_name} ({self.organization})"



class FundraiserBeneficiary(TenantScopedModel):
    """
    Explicit junction table linking a Fundraiser to a Beneficiary.
    Through model — never use implicit M2M for audit-grade relationships.
    organization is denormalized here intentionally (see decisions.md)
    for direct tenant-scoped queries without JOIN overhead.
    """

    fundraiser = models.ForeignKey(
        "Fundraiser",
        on_delete=models.PROTECT,
        related_name="beneficiary_links",
    )
    beneficiary = models.ForeignKey(
        "Beneficiary",
        on_delete=models.PROTECT,
        related_name="fundraiser_links",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="fundraiser_beneficiary_links",
        null=True,          # null=True because system actions may not have a user
        blank=True,
    )
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["fundraiser", "beneficiary"],
                name="unique_fundraiser_beneficiary",
            )
        ]
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.fundraiser} → {self.beneficiary}"
