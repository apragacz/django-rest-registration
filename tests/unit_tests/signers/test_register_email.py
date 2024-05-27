from django.test.utils import override_settings

from rest_registration.api.views.register_email import RegisterEmailSigner


def test_signer_with_different_secret_keys(
    settings_with_register_email_verification,
    user,
):
    email = 'testuser1@example.com'
    data_to_sign = {
        'user_id': user.pk,
        'email': email,
    }
    secrets = [
        '#0ka!t#6%28imjz+2t%l(()yu)tg93-1w%$du0*po)*@l+@+4h',
        'feb7tjud7m=91$^mrk8dq&nz(0^!6+1xk)%gum#oe%(n)8jic7',
    ]
    signatures = []
    for secret in secrets:
        with override_settings(
                SECRET_KEY=secret):
            signer = RegisterEmailSigner(data_to_sign)
            data = signer.get_signed_data()
            signatures.append(data[signer.SIGNATURE_FIELD])

    assert signatures[0] != signatures[1]
