from django.db import models

class Organization(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TenantManager(models.Manager):
    def get_queryset(self):
        # Tenant filtering logic goes here — placeholder for now.
        # Real thread-local lookup gets wired when the middleware exists (Day 2/3).
        return super().get_queryset()

class TenantScopedModel(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    objects = TenantManager()

    class Meta:
        abstract = True
