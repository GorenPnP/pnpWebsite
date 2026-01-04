import os

# essentially runs:
# $ python manage.py migrate
# $ python manage.py collectstatic --noinput
# $ daphne -b 0.0.0.0 -p 8000 ppServer.asgi:application

# see manage.py :)
# needed to copy some of it, because the hardened image used does not have a shell to run multiple commands after the db is ready
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ppServer.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(["manage.py", "migrate"])
    execute_from_command_line(["manage.py", "collectstatic", "--noinput"])
    execute_from_command_line(["manage.py", "runserver", "0.0.0.0:80"])