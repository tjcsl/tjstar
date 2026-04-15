uv sync --frozen
uv run manage.py makemigrations adminpanel lookup
uv run manage.py migrate

while true
do
    uv run manage.py runserver 0.0.0.0:8000
    sleep 1
done