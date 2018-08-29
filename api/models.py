from django.db import models


class Review(models.Model):
    title = models.CharField(max_length=64)
    summary = models.CharField(max_length=10000)
    rating = models.PositiveIntegerField()
    ip_address = models.GenericIPAddressField()
    company = models.CharField(max_length=24)
    reviewer = models.CharField(max_length=24)
    created_at = models.DateTimeField(auto_now=True)
