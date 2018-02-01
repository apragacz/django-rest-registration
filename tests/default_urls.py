from django.conf.urls import include, url

api_urlpatterns = [
    url('accounts/', include('rest_registration.api.urls')),
]

urlpatterns = [
    url('api/', include(api_urlpatterns)),
]
