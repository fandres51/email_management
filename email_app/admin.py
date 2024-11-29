from django.contrib import admin
from .models import Email

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'date', 'company_of_sender', 'unique_email_code', 'content')
