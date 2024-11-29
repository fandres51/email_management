from django.urls import path
from . import views

urlpatterns = [
    path('', views.email_list, name='email_list'),
    path('upload', views.upload_emails, name='upload_emails'),
    path('delete-email/<int:email_id>/', views.delete_email, name='delete_email'),
]