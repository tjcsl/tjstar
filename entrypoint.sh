uv sync --frozen
uv run manage.py makemigrations adminpanel lookup
uv run manage.py migrate

if [ ! -f "first_run.log" ]; then
    uv run manage.py populate_test_data
    touch first_run.log
    export DJANGO_SUPERUSER_PASSWORD=123
    uv run manage.py createsuperuser --username admin --email admin@example.com --noinput
    uv run manage.py shell << 'PYEOF'
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from tjstar.apps.lookup.models import Presentation

group = Group.objects.create(name='admins')
content_type = ContentType.objects.get_for_model(Presentation)

perms = Permission.objects.filter(
    content_type=content_type,
    codename__in=['add_presentation', 'change_presentation', 'delete_presentation', 'view_presentation']
)
for perm in perms:
    group.permissions.add(perm)
PYEOF
fi

while true
do
    uv run manage.py runserver 0.0.0.0:8000
    sleep 1
done