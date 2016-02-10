from django.conf.urls import url

from .views import (change_password, login, logout, profile,
                    send_reset_password_link, reset_password,
                    register, verify_registration,
                    register_email, verify_email)


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
