from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime, timedelta
from django.utils import timezone

# Create your models here.
class EmailVerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)
