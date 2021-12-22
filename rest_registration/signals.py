"""
Custom signals sent during the registration and activation processes.
"""

from django.dispatch import Signal

# A new user has registered.
user_registered = Signal()

# A user has activated his or her account.
user_activated = Signal()

# A user has verified his or her new email.
user_changed_email = Signal()
