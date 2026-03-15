#!/usr/bin/env bash
set -o errexit

echo "🚀 Building StudentBuddy for production deployment..."

# Install dependencies
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
cd core
python manage.py collectstatic --noinput

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

echo "✅ Build complete!"
