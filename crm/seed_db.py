from crm.models import Customer, Product

def run():
    Customer.objects.bulk_create([
        Customer(name="Alice", email="alice@example.com", phone="+1234567890"),
        Customer(name="Bob", email="bob@example.com", phone="123-456-7890"),
        Customer(name="Carol", email="carol@example.com")
    ])

    Product.objects.bulk_create([
        Product(name="Laptop", price=999.99, stock=10),
        Product(name="Mouse", price=19.99, stock=100)
    ])
