from django.urls import path

from .views import (
    change_password,
    login,
    logout,
    profile,
    register,
    register_email,
    reset_password,
    send_reset_password_link,
    verify_email,
    verify_registration
)

app_name = 'rest_registration'
urlpatterns = [
    path('register/', register, name='register'),
    path('verify-registration/', verify_registration, name='verify-registration'),

    path(
        'send-reset-password-link/', send_reset_password_link,
        name='send-reset-password-link',
    ),
    path('reset-password/', reset_password, name='reset-password'),

    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),

    path('profile/', profile, name='profile'),

    path('change-password/', change_password, name='change-password'),

    path('register-email/', register_email, name='register-email'),
    path('verify-email/', verify_email, name='verify-email'),
]
