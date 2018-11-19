HTML e-mail configuration
=========================

You can send the verification emails as HTML, by specifying
``html_body`` instead of ``body``; for example:

.. code:: python

    REST_REGISTRATION = {
        ...

        'REGISTER_VERIFICATION_EMAIL_TEMPLATES': {
            'subject':  'rest_registration/register/subject.txt',
            'html_body':  'rest_registration/register/body.html',
        },

        ...
    }

This will automatically create fallback plain text message from the
HTML. If you want to have custom fallback message you can also provide
separate template for text:

.. code:: python

    REST_REGISTRATION = {
        ...

        'REGISTER_VERIFICATION_EMAIL_TEMPLATES': {
            'subject':  'rest_registration/register/subject.txt',
            'text_body':  'rest_registration/register/body.txt',
            'html_body':  'rest_registration/register/body.html',
        },

        ...
    }
