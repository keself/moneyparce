from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class Transaction(models.Model):
    ACTION_CHOICES = [
        ('add', 'Add'),
        ('remove', 'Remove'),
    ]
    
    # each transaction associated w a specific user
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # stores amt of the transaction
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # either add or remove choices
    action = models.CharField(max_length=6, choices=ACTION_CHOICES)
    # time of transaction
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} {self.amount} by {self.user.username} on {self.timestamp}"