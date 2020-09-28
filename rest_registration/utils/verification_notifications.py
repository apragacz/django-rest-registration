
from rest_registration.notifications.email import send_verification_notification
from rest_registration.notifications.enums import NotificationType
from rest_registration.settings import registration_settings
from rest_registration.signers.register import RegisterSigner
from rest_registration.utils.users import get_user_verification_id


def send_register_verification_email_notification(request, user):
    signer = RegisterSigner({
        'user_id': get_user_verification_id(user),
    }, request=request)
    template_config_data = registration_settings.REGISTER_VERIFICATION_EMAIL_TEMPLATES
    notification_data = {
        'params_signer': signer,
    }
    send_verification_notification(
        NotificationType.REGISTER_VERIFICATION, user,
        notification_data, template_config_data)
