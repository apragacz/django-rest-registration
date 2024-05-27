from django.urls import include, path

urlpatterns = [
    path("accounts/", include("rest_registration.contrib.verification_redirects.urls")),
]
