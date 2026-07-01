from django.db import models
from django.conf import settings


class Organization(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name




class Membership(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MEMBER = 'member', 'Member'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'organization')

    def __str__(self):
        return f"{self.user} @ {self.organization} ({self.role})"




class TenantManager(models.Manager):
    def get_queryset(self):
        raise NotImplementedError(
            "TenantManager has no filtering logic yet (ADR-004). "
            "Do not use TenantScopedModel subclasses until middleware "
            "sets the current-organization context. See DECISIONS.md ADR-004."
        )



class TenantScopedModel(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    objects = TenantManager()

    class Meta:
        abstract = True
