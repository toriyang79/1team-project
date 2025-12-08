#!/bin/bash
set -e

echo "Starting Media Platform..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until pg_isready -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" -U "${DB_USER:-postgres}" > /dev/null 2>&1; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done
echo "PostgreSQL is ready!"

# Wait for Redis to be ready (if using Redis)
if [ -n "$REDIS_URL" ]; then
  echo "Waiting for Redis..."
  REDIS_HOST=$(echo $REDIS_URL | sed -E 's|redis://([^:]+):.*|\1|')
  REDIS_PORT=$(echo $REDIS_URL | sed -E 's|.*:([0-9]+)/.*|\1|')
  until nc -z $REDIS_HOST $REDIS_PORT > /dev/null 2>&1; do
    echo "Redis is unavailable - sleeping"
    sleep 1
  done
  echo "Redis is ready!"
fi

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed (in development)
if [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "Creating superuser..."
  python manage.py shell -c "
from apps.users.models import User
if not User.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists():
    User.objects.create_superuser(
        email='$DJANGO_SUPERUSER_EMAIL',
        password='$DJANGO_SUPERUSER_PASSWORD',
        nickname='admin'
    )
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"
fi

echo "Starting application..."
exec "$@"
