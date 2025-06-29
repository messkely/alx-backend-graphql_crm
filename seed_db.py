import os
import django
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order


def seed_database():
    print("Seeding database...")
    
    # Clear existing data
    Order.objects.all().delete()
    Customer.objects.all().delete()
    Product.objects.all().delete()
    
    # Create customers
    customers = [
        Customer.objects.create(
            name="Alice Johnson",
            email="alice@example.com",
            phone="+1234567890"
        ),
        Customer.objects.create(
            name="Bob Smith",
            email="bob@example.com",
            phone="123-456-7890"
        ),
        Customer.objects.create(
            name="Carol Davis",
            email="carol@example.com",
            phone="+1987654321"
        ),
        Customer.objects.create(
            name="David Wilson",
            email="david@example.com"
        ),
        Customer.objects.create(
            name="Eve Brown",
            email="eve@example.com",
            phone="555-123-4567"
        ),
    ]
    
    # Create products
    products = [
        Product.objects.create(
            name="Laptop",
            price=Decimal("999.99"),
            stock=10
        ),
        Product.objects.create(
            name="Mouse",
            price=Decimal("29.99"),
            stock=50
        ),
        Product.objects.create(
            name="Keyboard",
            price=Decimal("79.99"),
            stock=25
        ),
        Product.objects.create(
            name="Monitor",
            price=Decimal("299.99"),
            stock=15
        ),
        Product.objects.create(
            name="Headphones",
            price=Decimal("149.99"),
            stock=8  # Low stock for testing
        ),
        Product.objects.create(
            name="Webcam",
            price=Decimal("89.99"),
            stock=5  # Low stock for testing
        ),
    ]
    
    # Create orders
    orders = [
        # Alice's orders
        Order.objects.create(customer=customers[0]),  # Alice - Laptop + Mouse
        Order.objects.create(customer=customers[0]),  # Alice - Keyboard
        
        # Bob's orders
        Order.objects.create(customer=customers[1]),  # Bob - Monitor + Headphones
        
        # Carol's orders
        Order.objects.create(customer=customers[2]),  # Carol - Laptop + Monitor
        
        # David's orders
        Order.objects.create(customer=customers[3]),  # David - Mouse + Keyboard + Headphones
    ]
    
    # Add products to orders
    orders[0].products.set([products[0], products[1]])  # Laptop + Mouse
    orders[1].products.set([products[2]])  # Keyboard
    orders[2].products.set([products[3], products[4]])  # Monitor + Headphones
    orders[3].products.set([products[0], products[3]])  # Laptop + Monitor
    orders[4].products.set([products[1], products[2], products[4]])  # Mouse + Keyboard + Headphones
    
    # Recalculate totals for all orders
    for order in orders:
        order.save()
    
    print(f"Created {len(customers)} customers")
    print(f"Created {len(products)} products")
    print(f"Created {len(orders)} orders")
    print("Database seeded successfully!")


if __name__ == "__main__":
    seed_database()