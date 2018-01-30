from django.conf.urls import url

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
    url('register/$', register, name='register'),
    url('verify-registration/$', verify_registration, name='verify-registration'),

    url('send-reset-password-link/$', send_reset_password_link, name='send-reset-password-link'),
    url('reset-password/$', reset_password, name='reset-password'),

    url('login/$', login, name='login'),
    url('logout/$', logout, name='logout'),

    url('profile/$', profile, name='profile'),

    url('change-password/$', change_password, name='change_password'),

    url('register-email/$', register_email, name='register-email'),
    url('verify-email/$', verify_email, name='verify-email'),
]  # noqa
