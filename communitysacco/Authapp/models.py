from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class MemberProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    membership_number = models.CharField(max_length=20, unique=True)
    joined_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.membership_number})"
