import os
import django
import random
from datetime import datetime

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "graphql_crm.settings")
django.setup()

from crm.models import Customer, Product, Order

def seed_customers():
    customers = [
        {"name": "Alice", "email": "alice@example.com", "phone": "+1234567890"},
        {"name": "Bob", "email": "bob@example.com", "phone": "123-456-7890"},
        {"name": "Carol", "email": "carol@example.com", "phone": None},
    ]

    for data in customers:
        customer, created = Customer.objects.get_or_create(email=data["email"], defaults=data)
        if created:
            print(f"Created customer: {customer.name}")
        else:
            print(f"Customer already exists: {customer.email}")

def seed_products():
    products = [
        {"name": "Laptop", "price": 999.99, "stock": 10},
        {"name": "Smartphone", "price": 499.99, "stock": 20},
        {"name": "Tablet", "price": 299.99, "stock": 15},
    ]

    for data in products:
        product, created = Product.objects.get_or_create(name=data["name"], defaults=data)
        if created:
            print(f"Created product: {product.name}")
        else:
            print(f"Product already exists: {product.name}")

def seed_orders():
    customers = list(Customer.objects.all())
    products = list(Product.objects.all())

    if not customers or not products:
        print("Customers or products not found. Seed them first.")
        return

    for i in range(3):  # create 3 sample orders
        customer = random.choice(customers)
        selected_products = random.sample(products, k=2)

        order = Order.objects.create(
            customer=customer,
            order_date=datetime.now()
        )
        order.products.set(selected_products)

        order.total_amount = sum(product.price for product in selected_products)
        order.save()

        print(f"Created order #{order.id} for {customer.name} with total: {order.total_amount:.2f}")

if __name__ == "__main__":
    print("Seeding database...")
    seed_customers()
    seed_products()
    seed_orders()
    print("Done!")