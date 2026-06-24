from django.db import models

# Create your models here.
class Lead(models.Model):
	email = models.EmailField(max_length=255, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)
