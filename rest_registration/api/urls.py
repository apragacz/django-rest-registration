from django.conf.urls import url

from .login_views import login, logout


urlpatterns = [
    url('login/$', login),
    url('logout/$', logout),
]
