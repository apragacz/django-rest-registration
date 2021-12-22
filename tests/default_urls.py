from django.urls import include, path

api_urlpatterns = [
    path('accounts/', include('rest_registration.api.urls')),
]

urlpatterns = [
    path('api/', include(api_urlpatterns)),
]
