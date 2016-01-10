from django.conf.urls import url

from .login_views import login, logout
from .register_views import register, verify_registration
from .profile_views import profile


urlpatterns = [
    url('login/$', login),
    url('logout/$', logout),
    url('register/$', register),
    url('verify-registration/$', verify_registration),
    url('profile/$', profile),
]
