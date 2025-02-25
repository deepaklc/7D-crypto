from django.urls import path
from . import views

urlpatterns = [
    path('send-email/', views.email_view, name='send_email'),  # URL for the email form
]
