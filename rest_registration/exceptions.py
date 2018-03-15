from rest_framework.exceptions import APIException


class BadRequest(APIException):
    status_code = 400
    default_detail = 'Bad Request'


class UserNotFound(APIException):
    status_code = 404
    default_detail = 'User not found'
