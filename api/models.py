from django.db import models


class Review(models.Model):
    title = models.CharField(max_length=24)
    summary = models.CharField(max_length=24)
    rating = models.IntegerField()
    ip_address = models.CharField(max_length=24)
    company = models.CharField(max_length=24)
    reviewer = models.CharField(max_length=24)
    created_at = models.DateTimeField(auto_now=True)
