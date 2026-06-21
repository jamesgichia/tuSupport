from django.db import models

class Organization(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

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
