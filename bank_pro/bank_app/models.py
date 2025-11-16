from django.db import models
import random

# Create your models here.

class Account(models.Model):
    ACCOUNT_TYPES = [
        ("SAVINGS", "Savings"),
        ("CURRENT", "Current"),
        ("SALARY", "Salary"),
        ("FD", "Fixed Deposit"),
    ]

    name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=16,primary_key=True, unique=True, editable=False)
    phone = models.CharField(max_length=10)
    email = models.EmailField()
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default="SAVINGS")
    balance = models.FloatField(default=0)
    ifsc_code = models.CharField(max_length=11, default="SFC00020911")
    branch_name = models.CharField(max_length=50, default="Main Branch")
    created_at = models.DateTimeField(auto_now_add=True)
    photo = models.URLField(default="Empty")


    def save(self, *args, **kwargs):
        if not self.account_number:
            # realistic 12-digit number prefixed
            self.account_number = "SFC" + str(random.randint(10000000, 99999999))
        super().save(*args, **kwargs)

class User(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # hashed password
    role = models.CharField(max_length=10, default="user")  # "admin" or "user"
