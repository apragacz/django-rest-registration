from rest_framework.authentication import SessionAuthentication


class SessionCSRFAuthentication(SessionAuthentication):

    def authenticate(self, request):
        user = getattr(request._request, 'user', None)  # noqa: E501 pylint: disable=protected-access
        self.enforce_csrf(request)
        return (user, None)
