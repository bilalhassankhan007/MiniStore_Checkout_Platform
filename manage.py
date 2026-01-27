# Why: manage.py is Django’s CLI entry point for migrations, running server, shell, etc.
# Keep it minimal and standard so anyone can run the project quickly.

#!/usr/bin/env python
import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
