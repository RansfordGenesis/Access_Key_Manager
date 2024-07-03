# models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

class AccessKey(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    key = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    date_of_procurement = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expiry_date:
            self.expiry_date = timezone.now() + timezone.timedelta(days=4*30)  # Approx. 4 months
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.key} ({self.status})"
