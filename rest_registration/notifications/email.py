from django.core.mail.message import EmailMessage
from django.template.loader import get_template

from rest_registration.settings import registration_settings
from rest_registration.utils import get_user_setting


def send_verification(user, params_signer, template_config, email=None):
    if email is None:
        email_field = get_user_setting('EMAIL_FIELD')
        email = getattr(user, email_field)
    body_template = get_template(template_config['body'])
    subject_template = get_template(template_config['subject'])
    from_email = registration_settings.VERIFICATION_FROM_EMAIL
    reply_to_email = (registration_settings.VERIFICATION_REPLY_TO_EMAIL or
                      from_email)
    ctx = {
        'user': user,
        'email': email,
        'verification_url':  params_signer.get_url(),
    }
    subject = subject_template.render(ctx).strip()
    body = body_template.render(ctx)

    email_msg = EmailMessage(
        subject, body,
        from_email, [email], reply_to=[reply_to_email],
    )
    email_msg.send()
