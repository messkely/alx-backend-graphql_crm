import graphene
from graphene_django.types import DjangoObjectType
from .models import Customer, Product, Order
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
from datetime import datetime

# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int()

# CreateCustomer Mutation
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        try:
            validate_email(input.email)
        except ValidationError:
            raise Exception("Invalid email format")

        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists")

        if input.phone:
            if not re.match(r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$', input.phone):
                raise Exception("Invalid phone format")

        customer = Customer(name=input.name, email=input.email, phone=input.phone)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully")

# BulkCreateCustomers Mutation
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created_customers = []
        errors = []
        for customer_data in input:
            try:
                validate_email(customer_data.email)
                if Customer.objects.filter(email=customer_data.email).exists():
                    raise Exception("Email already exists")
                if customer_data.phone and not re.match(r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$', customer_data.phone):
                    raise Exception("Invalid phone format")
                customer = Customer(name=customer_data.name, email=customer_data.email, phone=customer_data.phone)
                customer.save()
                created_customers.append(customer)
            except Exception as e:
                errors.append(f"{customer_data.email}: {str(e)}")
        return BulkCreateCustomers(customers=created_customers, errors=errors)

# CreateProduct Mutation
class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        if input.price <= 0:
            raise Exception("Price must be positive")
        if input.stock is not None and input.stock < 0:
            raise Exception("Stock cannot be negative")
        product = Product(name=input.name, price=input.price, stock=input.stock or 0)
        product.save()
        return CreateProduct(product=product)

# CreateOrder Mutation
class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime()

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")

        products = Product.objects.filter(pk__in=product_ids)
        if not products.exists():
            raise Exception("No valid products found")

        total_amount = sum(p.price for p in products)
        order = Order.objects.create(customer=customer, order_date=order_date or datetime.now(), total_amount=total_amount)
        order.products.set(products)
        order.save()

        return CreateOrder(order=order)

# Query Class
class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")

# Mutation Class
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
