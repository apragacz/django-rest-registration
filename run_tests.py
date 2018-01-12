#!/usr/bin/env python
import sys

from tests.utils import configure_settings
from django.core.management import execute_from_command_line


def main(args):
    configure_settings()
    cmd_args = args[0:1] + ['test'] + args[1:]
    execute_from_command_line(cmd_args)


if __name__ == '__main__':
    main(sys.argv)
