from django.core.mail.message import EmailMessage
from django.template.loader import get_template

from rest_registration.settings import registration_settings


def send(email, params_signer):
    config = registration_settings.REGISTER_VERIFICATION_EMAIL_TEMPLATES
    ctx = {
        'verification_url':  params_signer.get_url(),
    }
    body_template = get_template(config['body'])
    subject_template = get_template(config['subject'])
    from_email = registration_settings.VERIFICATION_FROM_EMAIL
    reply_to_email = (registration_settings.VERIFICATION_REPLY_TO_EMAIL
                      or from_email)
    subject = subject_template.render(ctx).strip()
    body = body_template.render(ctx)

    email_msg = EmailMessage(
        subject, body,
        from_email, [email], reply_to=[reply_to_email],
    )
    email_msg.send()
