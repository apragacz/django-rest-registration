#!/usr/bin/env python
import sys
import os.path

from django.conf import settings
from django.core.management import execute_from_command_line


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def configure_settings():
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(BASE_DIR, 'test_db.sqlite3'),
            }
        },
        INSTALLED_APPS=(
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',

            'rest_framework',
            'rest_registration',
        ),
        TEMPLATES=(
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [],
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.template.context_processors.debug',
                        'django.template.context_processors.request',
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages',
                    ],
                },
            },
        )
    )


def main(args):
    configure_settings()
    cmd_args = args[0:1] + ['test'] + args[1:]
    execute_from_command_line(cmd_args)


if __name__ == '__main__':
    main(sys.argv)
