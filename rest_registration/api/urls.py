from django.conf.urls import url

from .login_views import login, logout
from .register_views import register
from .profile_views import profile


urlpatterns = [
    url('login/$', login),
    url('logout/$', logout),
    url('register/$', register),
    url('profile/$', profile),
]
