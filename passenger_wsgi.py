import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'virtualshope.settings')

import django

django.setup()

from django.core.management import call_command

# Sin acceso a terminal en este hosting, migrar/recolectar estáticos/crear el superusuario
# se hace aquí, una vez por arranque de la app. Todas estas operaciones son seguras de repetir.
call_command('migrate', interactive=False, verbosity=0)
call_command('collectstatic', interactive=False, verbosity=0)

from django.contrib.auth import get_user_model

User = get_user_model()
_su_username = os.environ.get('DJANGO_SUPERUSER_USERNAME', '')
_su_password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')
if _su_username and _su_password and not User.objects.filter(username=_su_username).exists():
    User.objects.create_superuser(
        username=_su_username,
        email=os.environ.get('DJANGO_SUPERUSER_EMAIL', ''),
        password=_su_password,
    )

from virtualshope.wsgi import application
