from rest_registration.settings import registration_settings
from rest_registration.utils.signers import URLParamsSigner
from rest_registration.utils.users import get_user_by_verification_id


class ResetPasswordSigner(URLParamsSigner):
    SALT_BASE = 'reset-password'
    USE_TIMESTAMP = True

    def get_base_url(self):
        return registration_settings.RESET_PASSWORD_VERIFICATION_URL

    def get_valid_period(self):
        return registration_settings.RESET_PASSWORD_VERIFICATION_PERIOD

    def _calculate_salt(self, data):
        if registration_settings.RESET_PASSWORD_VERIFICATION_ONE_TIME_USE:
            user = get_user_by_verification_id(data['user_id'], require_verified=False)
            user_password_hash = user.password
            # Use current user password hash as a part of the salt.
            # If the password gets changed, then assume that the change
            # was caused by previous password reset and the signature
            # is not valid anymore because changed password hash implies
            # changed salt used when verifying the input data.
            salt = '{self.SALT_BASE}:{user_password_hash}'.format(
                self=self, user_password_hash=user_password_hash)
        else:
            salt = self.SALT_BASE
        return salt
