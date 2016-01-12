from django.conf.urls import url

from .change_password_views import change_password
from .login_views import login, logout
from .profile_views import profile
from .register_views import register, verify_registration


urlpatterns = [
    url('login/$', login),
    url('logout/$', logout),
    url('register/$', register),
    url('verify-registration/$', verify_registration),
    url('profile/$', profile),
    url('change-password/$', change_password),
]
