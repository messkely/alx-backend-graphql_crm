#!/bin/bash

# ALX Backend GraphQL CRM Setup Script

echo "Setting up ALX Backend GraphQL CRM..."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create migrations
echo "Creating migrations..."
python manage.py makemigrations crm

# Apply migrations
echo "Applying migrations..."
python manage.py migrate

# Seed database
echo "Seeding database with sample data..."
python seed_db.py

echo "Setup complete!"
echo "Run 'python manage.py runserver' to start the development server."
echo "Visit http://localhost:8000/graphql/ to access the GraphQL interface."