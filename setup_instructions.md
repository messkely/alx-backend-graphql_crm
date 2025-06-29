# GraphQL CRM System Setup Instructions

## Prerequisites
- Python 3.8+
- Django 4.0+
- pip package manager

## Installation Steps

### 1. Create Django Project
```bash
# Create the project
django-admin startproject alx_backend_graphql_crm
cd alx_backend_graphql_crm

# Create the CRM app
python manage.py startapp crm
```

### 2. Install Required Packages
```bash
pip install django graphene-django django-filter
```

### 3. File Structure
Your project should have the following structure:
```
alx_backend_graphql_crm/
├── alx_backend_graphql_crm/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── schema.py
│   └── wsgi.py
├── crm/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── schema.py
│   ├── filters.py
│   └── migrations/
├── seed_db.py
└── manage.py
```

### 4. Database Setup
```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Seed database with sample data
python manage.py shell < seed_db.py
```

### 5. Run the Server
```bash
python manage.py runserver
```

### 6. Access GraphQL Interface
Navigate to: `http://localhost:8000/graphql/`

You should see the GraphiQL interface where you can test your GraphQL queries and mutations.

## Testing the Setup

### Basic Query
```graphql
{
  hello
}
```

### Create a Customer
```graphql
mutation {
  createCustomer(input: {
    name: "John Doe"
    email: "john@example.com"
    phone: "+1234567890"
  }) {
    customer {
      id
      name
      email
      phone
    }
    message
    errors
  }
}
```

### Query All Customers with Filtering
```graphql
query {
  allCustomers(filter: {nameIcontains: "Alice"}) {
    edges {
      node {
        id
        name
        email
        phone