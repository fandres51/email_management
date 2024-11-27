from django.db import models
from uuid import uuid4

class Email(models.Model):
    recipient = models.EmailField(max_length=254)
    sender = models.EmailField(max_length=254)
    date = models.DateTimeField(auto_now_add=True)
    company_of_sender = models.CharField(max_length=100)
    unique_email_code = models.UUIDField(default=uuid4, editable=False, unique=True, max_length=64)

    def __str__(self):
        return f'{self.sender} envió un email a {self.recipient} el {self.date}'
