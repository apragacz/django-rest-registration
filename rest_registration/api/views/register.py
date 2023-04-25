from typing import Type

from django.db import transaction
from django.http import Http404
from django.utils.translation import gettext as _
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from rest_registration import signals
from rest_registration.api.views.base import BaseAPIView
from rest_registration.api.views.login import perform_login
from rest_registration.exceptions import UserWithoutEmailNonverifiable
from rest_registration.settings import registration_settings
from rest_registration.signers.register import RegisterSigner
from rest_registration.utils.responses import get_ok_response
from rest_registration.utils.users import (
    get_user_by_verification_id,
    get_user_email_field_name,
    get_user_setting
)
from rest_registration.utils.verification import verify_signer_or_bad_request


class RegisterView(BaseAPIView):
    permission_classes = registration_settings.NOT_AUTHENTICATED_PERMISSION_CLASSES

    def post(self, request: Request) -> Response:
        '''
        Register new user.
        '''
        if not registration_settings.REGISTER_FLOW_ENABLED:
            raise Http404()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        kwargs = {}

        if registration_settings.REGISTER_VERIFICATION_ENABLED:
            verification_flag_field = get_user_setting('VERIFICATION_FLAG_FIELD')
            kwargs[verification_flag_field] = False
            email_field_name = get_user_email_field_name()
            if (email_field_name not in serializer.validated_data
                    or not serializer.validated_data[email_field_name]):
                raise UserWithoutEmailNonverifiable()

        with transaction.atomic():
            user = serializer.save(**kwargs)
            if registration_settings.REGISTER_VERIFICATION_ENABLED:
                email_sender = registration_settings.REGISTER_VERIFICATION_EMAIL_SENDER
                email_sender(request, user)

        signals.user_registered.send(sender=None, user=user, request=request)
        output_serializer_class = registration_settings.REGISTER_OUTPUT_SERIALIZER_CLASS
        output_serializer = output_serializer_class(
            instance=user,
            context={'request': request},
        )
        user_data = output_serializer.data
        return Response(user_data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self) -> Type[Serializer]:
        return registration_settings.REGISTER_SERIALIZER_CLASS


register = RegisterView.as_view()


class VerifyRegistrationSerializer(serializers.Serializer):  # noqa: E501 pylint: disable=abstract-method
    user_id = serializers.CharField(required=True)
    timestamp = serializers.IntegerField(required=True)
    signature = serializers.CharField(required=True)


class VerifyRegistrationView(BaseAPIView):
    permission_classes = registration_settings.NOT_AUTHENTICATED_PERMISSION_CLASSES

    def post(self, request: Request) -> Response:
        """
        Verify registration via signature.
        """
        user = process_verify_registration_data(
            request.data,
            serializer_context=self.get_serializer_context(),
        )
        signals.user_activated.send(sender=None, user=user, request=request)
        extra_data = None
        if registration_settings.REGISTER_VERIFICATION_AUTO_LOGIN:
            extra_data = perform_login(request, user)
        return get_ok_response(_("User verified successfully"), extra_data=extra_data)

    def get_serializer_class(self) -> Type[Serializer]:
        return VerifyRegistrationSerializer


verify_registration = VerifyRegistrationView.as_view()


def process_verify_registration_data(input_data, serializer_context=None):
    if serializer_context is None:
        serializer_context = {}
    if not registration_settings.REGISTER_VERIFICATION_ENABLED:
        raise Http404()
    serializer = VerifyRegistrationSerializer(
        data=input_data,
        context=serializer_context,
    )
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data
    # We use the signer only for verification, therefore we don't need a base_url and
    # may set strict=False
    signer = RegisterSigner(data, strict=False)
    verify_signer_or_bad_request(signer)

    verification_flag_field = get_user_setting('VERIFICATION_FLAG_FIELD')
    user = get_user_by_verification_id(data['user_id'], require_verified=False)
    setattr(user, verification_flag_field, True)
    user.save()

    return user
