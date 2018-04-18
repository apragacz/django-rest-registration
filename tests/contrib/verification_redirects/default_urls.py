from django.conf.urls import include, url

urlpatterns = [
    url('accounts/',
        include('rest_registration.contrib.verification_redirects.urls')),
]
