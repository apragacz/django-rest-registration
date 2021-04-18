from rest_registration.settings import registration_settings
from rest_registration.utils.signers import URLParamsSigner


class RegisterEmailSigner(URLParamsSigner):
    SALT_BASE = 'register-email'
    USE_TIMESTAMP = True

    def get_base_url(self):
        return registration_settings.REGISTER_EMAIL_VERIFICATION_URL

    def get_valid_period(self):
        return registration_settings.REGISTER_EMAIL_VERIFICATION_PERIOD
