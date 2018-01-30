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
    url('register/$', register),
    url('verify-registration/$', verify_registration),

    url('send-reset-password-link/$', send_reset_password_link),
    url('reset-password/$', reset_password),

    url('login/$', login),
    url('logout/$', logout),

    url('profile/$', profile),

    url('change-password/$', change_password),

    url('register-email/$', register_email),
    url('verify-email/$', verify_email),
]  # noqa
