# crm/schema.py
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from decimal import Decimal
import re
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter

# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"
        interfaces = (graphene.relay.Node,)

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"
        interfaces = (graphene.relay.Node,)

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"
        interfaces = (graphene.relay.Node,)

# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

# Output Types
class CustomerOutput(graphene.ObjectType):
    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

class BulkCustomerOutput(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

class ProductOutput(graphene.ObjectType):
    product = graphene.Field(ProductType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

class OrderOutput(graphene.ObjectType):
    order = graphene.Field(OrderType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

class LowStockUpdateOutput(graphene.ObjectType):
    products = graphene.List(ProductType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

# Utility Functions
def validate_phone_format(phone):
    """Validate phone number format"""
    if not phone:
        return True
    
    # Patterns for +1234567890 or 123-456-7890
    patterns = [
        r'^\+\d{10,15}$',  # +1234567890
        r'^\d{3}-\d{3}-\d{4}$',  # 123-456-7890
        r'^\(\d{3}\) \d{3}-\d{4}$',  # (123) 456-7890
    ]
    
    return any(re.match(pattern, phone) for pattern in patterns)

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    Output = CustomerOutput

    def mutate(self, info, input):
        errors = []
        
        # Validate email format
        try:
            validate_email(input.email)
        except ValidationError:
            errors.append("Invalid email format")
        
        # Check email uniqueness
        if Customer.objects.filter(email=input.email).exists():
            errors.append("Email already exists")
        
        # Validate phone format
        if input.phone and not validate_phone_format(input.phone):
            errors.append("Invalid phone format. Use +1234567890 or 123-456-7890")
        
        if errors:
            return CustomerOutput(errors=errors)
        
        try:
            customer = Customer.objects.create(
                name=input.name,
                email=input.email,
                phone=input.phone
            )
            return CustomerOutput(
                customer=customer,
                message="Customer created successfully"
            )
        except Exception as e:
            return CustomerOutput(errors=[str(e)])

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    Output = BulkCustomerOutput

    def mutate(self, info, input):
        customers = []
        errors = []
        
        with transaction.atomic():
            for i, customer_data in enumerate(input):
                try:
                    # Validate email format
                    validate_email(customer_data.email)
                    
                    # Check email uniqueness
                    if Customer.objects.filter(email=customer_data.email).exists():
                        errors.append(f"Customer {i+1}: Email already exists")
                        continue
                    
                    # Validate phone format
                    if customer_data.phone and not validate_phone_format(customer_data.phone):
                        errors.append(f"Customer {i+1}: Invalid phone format")
                        continue
                    
                    customer = Customer.objects.create(
                        name=customer_data.name,
                        email=customer_data.email,
                        phone=customer_data.phone
                    )
                    customers.append(customer)
                    
                except ValidationError:
                    errors.append(f"Customer {i+1}: Invalid email format")
                except Exception as e:
                    errors.append(f"Customer {i+1}: {str(e)}")
        
        return BulkCustomerOutput(customers=customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    Output = ProductOutput

    def mutate(self, info, input):
        errors = []
        
        # Validate price is positive
        if input.price <= 0:
            errors.append("Price must be positive")
        
        # Validate stock is non-negative
        stock = input.stock if input.stock is not None else 0
        if stock < 0:
            errors.append("Stock cannot be negative")
        
        if errors:
            return ProductOutput(errors=errors)
        
        try:
            product = Product.objects.create(
                name=input.name,
                price=input.price,
                stock=stock
            )
            return ProductOutput(
                product=product,
                message="Product created successfully"
            )
        except Exception as e:
            return ProductOutput(errors=[str(e)])

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    Output = OrderOutput

    def mutate(self, info, input):
        errors = []
        
        # Validate customer exists
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            errors.append("Invalid customer ID")
            return OrderOutput(errors=errors)
        
        # Validate products exist and at least one is provided
        if not input.product_ids:
            errors.append("At least one product must be selected")
            return OrderOutput(errors=errors)
        
        products = Product.objects.filter(id__in=input.product_ids)
        if len(products) != len(input.product_ids):
            errors.append("One or more invalid product IDs")
            return OrderOutput(errors=errors)
        
        try:
            with transaction.atomic():
                order = Order.objects.create(
                    customer=customer,
                    order_date=input.order_date
                )
                order.products.set(products)
                
                # Calculate total amount
                total = sum(product.price for product in products)
                order.total_amount = total
                order.save()
                
                return OrderOutput(
                    order=order,
                    message="Order created successfully"
                )
        except Exception as e:
            return OrderOutput(errors=[str(e)])

class UpdateLowStockProducts(graphene.Mutation):
    """Update products with stock < 10 by incrementing stock by 10"""
    
    Output = LowStockUpdateOutput
    
    def mutate(self, info):
        errors = []
        updated_products = []
        
        try:
            # Find products with stock < 10
            low_stock_products = Product.objects.filter(stock__lt=10)
            
            if not low_stock_products.exists():
                return LowStockUpdateOutput(
                    products=[],
                    message="No products with low stock found"
                )
            
            # Update each product's stock
            for product in low_stock_products:
                old_stock = product.stock
                product.stock += 10
                product.save()
                updated_products.append(product)
            
            return LowStockUpdateOutput(
                products=updated_products,
                message=f"Successfully updated {len(updated_products)} products with low stock"
            )
            
        except Exception as e:
            return LowStockUpdateOutput(errors=[str(e)])

# Query Class
class Query(graphene.ObjectType):
    hello = graphene.String()
    
    # Single object queries
    customer = graphene.Field(CustomerType, id=graphene.ID(required=True))
    product = graphene.Field(ProductType, id=graphene.ID(required=True))
    order = graphene.Field(OrderType, id=graphene.ID(required=True))
    
    # Filtered list queries
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

    def resolve_hello(self, info):
        return "Hello, GraphQL!"
    
    def resolve_customer(self, info, id):
        try:
            return Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            return None
    
    def resolve_product(self, info, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            return None
    
    def resolve_order(self, info, id):
        try:
            return Order.objects.get(id=id)
        except Order.DoesNotExist:
            return None

# Mutation Class
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()