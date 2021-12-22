from django.urls import path

from .views import reset_password, verify_email, verify_registration

app_name = 'rest_registration.contrib.verification_redirects'
urlpatterns = [
    path('verify-registration/', verify_registration, name='verify-registration'),
    path('verify-email/', verify_email, name='verify-email'),
    path('reset-password/', reset_password, name='reset-password'),
]
