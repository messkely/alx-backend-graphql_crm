"""
Database seeding script for CRM system
Run this script to populate the database with sample data

Usage:
python manage.py shell < seed_db.py
"""

from crm.models import Customer, Product, Order
from decimal import Decimal
from django.db import transaction

def seed_database():
    """Populate database with sample data"""
    
    print("Starting database seeding...")
    
    with transaction.atomic():
        # Create sample customers
        customers_data = [
            {"name": "Alice Johnson", "email": "alice@example.com", "phone": "+1234567890"},
            {"name": "Bob Smith", "email": "bob@example.com", "phone": "123-456-7890"},
            {"name": "Carol Davis", "email": "carol@example.com", "phone": "+1987654321"},
            {"name": "David Wilson", "email": "david@example.com", "phone": "987-654-3210"},
            {"name": "Eve Brown", "email": "eve@example.com", "phone": "+1555666777"},
        ]
        
        customers = []
        for customer_data in customers_data:
            customer, created = Customer.objects.get_or_create(
                email=customer_data["email"],
                defaults=customer_data
            )
            customers.append(customer)
            if created:
                print(f"Created customer: {customer.name}")
        
        # Create sample products
        products_data = [
            {"name": "Laptop", "price": Decimal("999.99"), "stock": 15},
            {"name": "Mouse", "price": Decimal("29.99"), "stock": 50},
            {"name": "Keyboard", "price": Decimal("79.99"), "stock": 30},
            {"name": "Monitor", "price": Decimal("299.99"), "stock": 20},
            {"name": "Headphones", "price": Decimal("149.99"), "stock": 25},
            {"name": "Webcam", "price": Decimal("89.99"), "stock": 10},
            {"name": "Speakers", "price": Decimal("199.99"), "stock": 5},
        ]
        
        products = []
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data["name"],
                defaults=product_data
            )
            products.append(product)
            if created:
                print(f"Created product: {product.name}")
        
        # Create sample orders
        orders_data = [
            {"customer_index": 0, "product_indices": [0, 1]},  # Alice: Laptop + Mouse
            {"customer_index": 1, "product_indices": [2, 3]},  # Bob: Keyboard + Monitor
            {"customer_index": 2, "product_indices": [4]},     # Carol: Headphones
            {"customer_index": 3, "product_indices": [0, 2, 1]}, # David: Laptop + Keyboard + Mouse
            {"customer_index": 4, "product_indices": [5, 6]},  # Eve: Webcam + Speakers
        ]
        
        for i, order_data in enumerate(orders_data):
            customer = customers[order_data["customer_index"]]
            order_products = [products[j] for j in order_data["product_indices"]]
            
            # Check if order already exists
            existing_order = Order.objects.filter(
                customer=customer,
                products__in=order_products
            ).first()
            
            if not existing_order:
                order = Order.objects.create(customer=customer)
                order.products.set(order_products)
                
                # Calculate total
                total = sum(product.price for product in order_products)
                order.total_amount = total
                order.save()
                
                print(f"Created order #{order.id} for {customer.name}: ${order.total_amount}")
    
    print("Database seeding completed!")
    print(f"Total customers: {Customer.objects.count()}")
    print(f"Total products: {Product.objects.count()}")
    print(f"Total orders: {Order.objects.count()}")

# Run the seeding function
if __name__ == "__main__":
    seed_database()
else:
    # If run through Django shell
    seed_database()