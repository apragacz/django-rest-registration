from rest_registration.settings import registration_settings
from rest_registration.utils.signers import URLParamsSigner
from rest_registration.utils.users import get_user_by_verification_id, get_user_setting


class RegisterSigner(URLParamsSigner):
    SALT_BASE = 'register'
    USE_TIMESTAMP = True

    def get_base_url(self):
        return registration_settings.REGISTER_VERIFICATION_URL

    def get_valid_period(self):
        return registration_settings.REGISTER_VERIFICATION_PERIOD

    def _calculate_salt(self, data):
        if registration_settings.REGISTER_VERIFICATION_ONE_TIME_USE:
            user = get_user_by_verification_id(data['user_id'], require_verified=False)
            # Use current user verification flag as a part of the salt.
            # If the verification flag gets changed, then assume that
            # the change was caused by previous verification and the signature
            # is not valid anymore because changed user verification flag
            # implies changed salt used when verifying the input data.
            verification_flag_field = get_user_setting('VERIFICATION_FLAG_FIELD')
            verification_flag = getattr(user, verification_flag_field)
            salt = '{self.SALT_BASE}:{verification_flag}'.format(
                self=self, verification_flag=verification_flag)
        else:
            salt = self.SALT_BASE
        return salt
