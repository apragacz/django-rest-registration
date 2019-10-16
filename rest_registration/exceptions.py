from rest_framework.exceptions import APIException
try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    def _(text): 
    	return text

class BadRequest(APIException):
    status_code = 400
    default_detail = _('Bad Request')


class UserNotFound(APIException):
    status_code = 404
    default_detail = _('User not found')
