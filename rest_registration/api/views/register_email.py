from typing import Any, Dict, Optional

from django.http import Http404
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from rest_registration import signals
from rest_registration.decorators import (
    api_view_serializer_class,
    api_view_serializer_class_getter
)
from rest_registration.exceptions import EmailAlreadyRegistered
from rest_registration.settings import registration_settings
from rest_registration.signers.register_email import RegisterEmailSigner
from rest_registration.utils.responses import get_ok_response
from rest_registration.utils.users import (
    get_user_by_verification_id,
    get_user_email_field_name,
    is_user_email_field_unique,
    user_with_email_exists
)
from rest_registration.utils.verification import verify_signer_or_bad_request


@api_view_serializer_class_getter(
    lambda: registration_settings.REGISTER_EMAIL_SERIALIZER_CLASS)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_email(request: Request) -> Response:
    '''
    Register new email.
    '''
    user = request.user

    serializer_class = registration_settings.REGISTER_EMAIL_SERIALIZER_CLASS
    serializer = serializer_class(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)

    # TODO: Issue #114 - remove code supporting deprecated behavior
    get_email = getattr(serializer, 'get_email', None)
    if callable(get_email):
        email = get_email()
    else:
        email = serializer.validated_data['email']

    email_already_used = is_user_email_field_unique() and user_with_email_exists(email)

    if registration_settings.REGISTER_EMAIL_VERIFICATION_ENABLED:
        email_sender = registration_settings.REGISTER_EMAIL_VERIFICATION_EMAIL_SENDER
        email_sender(request, user, email, email_already_used=email_already_used)
    else:
        if email_already_used:
            raise EmailAlreadyRegistered()

        email_field_name = get_user_email_field_name()
        old_email = getattr(user, email_field_name)
        setattr(user, email_field_name, email)
        user.save()
        signals.user_changed_email.send(
            sender=None,
            user=user,
            new_email=email,
            old_email=old_email,
            request=request,
        )

    return get_ok_response(_("Register email link email sent"))


class VerifyEmailSerializer(serializers.Serializer):  # noqa: E501 pylint: disable=abstract-method
    user_id = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    timestamp = serializers.IntegerField(required=True)
    signature = serializers.CharField(required=True)


@api_view_serializer_class(VerifyEmailSerializer)
@api_view(['POST'])
@permission_classes(registration_settings.NOT_AUTHENTICATED_PERMISSION_CLASSES)
def verify_email(request: Request) -> Response:
    '''
    Verify email via signature.
    '''
    process_verify_email_data(request.data, serializer_context={'request': request})
    return get_ok_response(_("Email verified successfully"))


def process_verify_email_data(
        input_data: Dict[str, Any],
        serializer_context: Optional[Dict[str, Any]] = None) -> None:
    if serializer_context is None:
        serializer_context = {}
    if not registration_settings.REGISTER_EMAIL_VERIFICATION_ENABLED:
        raise Http404()
    serializer = VerifyEmailSerializer(data=input_data, context=serializer_context)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data
    # We use the signer only for verification, therefore we don't need a base_url and
    # may set strict=False
    signer = RegisterEmailSigner(data, strict=False)
    verify_signer_or_bad_request(signer)
    request = serializer_context.get('request')
    new_email = data['email']

    if is_user_email_field_unique() and user_with_email_exists(new_email):
        raise EmailAlreadyRegistered()

    email_field_name = get_user_email_field_name()
    user = get_user_by_verification_id(data['user_id'])
    old_email = getattr(user, email_field_name)
    setattr(user, email_field_name, new_email)
    user.save()

    signals.user_changed_email.send(
        sender=None,
        user=user,
        new_email=new_email,
        old_email=old_email,
        request=request,
    )
