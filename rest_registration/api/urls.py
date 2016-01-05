from django.conf.urls import url

from .login_views import login, logout
from .register_views import register


urlpatterns = [
    url('login/$', login),
    url('logout/$', logout),
    url('register/$', register),
]
