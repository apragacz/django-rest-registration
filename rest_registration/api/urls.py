from django.conf.urls import url

from .views import (change_password, login, logout, profile,
                    register, verify_registration)


urlpatterns = [
    url('login/$', login),
    url('logout/$', logout),
    url('register/$', register),
    url('verify-registration/$', verify_registration),
    url('profile/$', profile),
    url('change-password/$', change_password),
]  # noqa
