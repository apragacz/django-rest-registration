from typing import Type

from django.http import Http404
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from rest_registration.api.serializers import PasswordConfirmSerializerMixin
from rest_registration.api.views.base import BaseAPIView
from rest_registration.exceptions import UserNotFound
from rest_registration.settings import registration_settings
from rest_registration.signers.reset_password import ResetPasswordSigner
from rest_registration.utils.responses import get_ok_response
from rest_registration.utils.users import get_user_by_verification_id
from rest_registration.utils.validation import (
    run_validators,
    validate_password_with_user_id,
    validate_user_password_confirm,
)
from rest_registration.utils.verification import verify_signer_or_bad_request


class SendResetPasswordLinkView(BaseAPIView):
    permission_classes = registration_settings.NOT_AUTHENTICATED_PERMISSION_CLASSES

    def post(self, request: Request) -> Response:
        '''
        Send email with reset password link.
        '''
        if not registration_settings.RESET_PASSWORD_VERIFICATION_ENABLED:
            raise Http404()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if registration_settings.RESET_PASSWORD_FAIL_WHEN_USER_NOT_FOUND:
            success_message = _("Reset link sent")
        else:
            success_message = _("Reset link sent if the user exists in database")
        user_finder = registration_settings.SEND_RESET_PASSWORD_LINK_USER_FINDER
        try:
            user = user_finder(serializer.validated_data, serializer=serializer)
        except UserNotFound:
            if registration_settings.RESET_PASSWORD_FAIL_WHEN_USER_NOT_FOUND:
                raise
            return get_ok_response(success_message)
        email_sender = registration_settings.RESET_PASSWORD_VERIFICATION_EMAIL_SENDER
        email_sender(request, user)
        return get_ok_response(success_message)

    def get_serializer_class(self) -> Type[Serializer]:
        return registration_settings.SEND_RESET_PASSWORD_LINK_SERIALIZER_CLASS


send_reset_password_link = SendResetPasswordLinkView.as_view()


class ResetPasswordSerializer(  # pylint: disable=abstract-method
        PasswordConfirmSerializerMixin,
        serializers.Serializer):
    user_id = serializers.CharField(required=True)
    timestamp = serializers.IntegerField(required=True)
    signature = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def has_password_confirm_field(self):
        return registration_settings.RESET_PASSWORD_SERIALIZER_PASSWORD_CONFIRM

    def validate(self, attrs):
        validators = [
            validate_password_with_user_id,
        ]
        if self.has_password_confirm_field():
            validators.append(validate_user_password_confirm)
        run_validators(validators, attrs)
        return attrs


class ResetPasswordView(BaseAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = registration_settings.NOT_AUTHENTICATED_PERMISSION_CLASSES

    def post(self, request: Request) -> Response:
        '''
        Reset password, given the signature and timestamp from the link.
        '''
        process_reset_password_data(
            request.data,
            serializer_context=self.get_serializer_context(),
        )
        return get_ok_response(_("Reset password successful"))


reset_password = ResetPasswordView.as_view()


def process_reset_password_data(input_data, serializer_context=None):
    if serializer_context is None:
        serializer_context = {}
    if not registration_settings.RESET_PASSWORD_VERIFICATION_ENABLED:
        raise Http404()
    serializer = ResetPasswordSerializer(data=input_data, context=serializer_context)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data.copy()
    password = data.pop('password')
    data.pop('password_confirm', None)
    # We use the signer only for verification, therefore we don't need a base_url and
    # may set strict=False
    signer = ResetPasswordSigner(data, strict=False)
    verify_signer_or_bad_request(signer)

    user = get_user_by_verification_id(data['user_id'], require_verified=False)
    user.set_password(password)
    user.save()
