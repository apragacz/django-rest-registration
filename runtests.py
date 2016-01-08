#!/usr/bin/env python
import sys
import os.path

from django.conf import settings
from django.core.management import execute_from_command_line


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main(args):
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(BASE_DIR, 'test_db.sqlite3'),
            }
        },
    )
    cmd_args = args[0:1] + ['test'] + args[1:]
    execute_from_command_line(cmd_args)


if __name__ == '__main__':
    main(sys.argv)
