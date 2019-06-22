"""
Custom signals sent during the registration and activation processes.
"""

from django.dispatch import Signal

# A new user has registered.
user_registered = Signal(providing_args=['user', 'request'])
# A user has verified / activated his or her account.
user_verified = Signal(providing_args=['user', 'request'])
# Alias for backward compatibility
user_activated = user_verified

user_logged_in = Signal(providing_args=['user', 'request'])
user_logged_out = Signal(providing_args=['user', 'request'])

user_password_reset_requested = Signal(providing_args=['user', 'request'])
user_password_changed = Signal(
    providing_args=['user', 'password', 'request'])

user_profile_updated = Signal(
    providing_args=['user', 'changed_data', 'request'])

user_email_registered = Signal(
    providing_args=['user', 'email', 'old_emails', 'request'])
user_email_verified = Signal(
    providing_args=['user', 'email', 'old_emails', 'request'])
