import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal
import re
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter


# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (graphene.relay.Node,)
        filterset_class = CustomerFilter


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)
        filterset_class = ProductFilter


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (graphene.relay.Node,)
        filterset_class = OrderFilter


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


# Mutation Response Types
class CreateCustomerResponse(graphene.ObjectType):
    customer = graphene.Field(CustomerType)
    message = graphene.String()
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)


class BulkCreateCustomersResponse(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    success_count = graphene.Int()
    error_count = graphene.Int()


class CreateProductResponse(graphene.ObjectType):
    product = graphene.Field(ProductType)
    message = graphene.String()
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)


class CreateOrderResponse(graphene.ObjectType):
    order = graphene.Field(OrderType)
    message = graphene.String()
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)


# Validation Functions
def validate_phone(phone):
    if phone:
        pattern = r'^\+?\d{10,15}$|^\d{3}-\d{3}-\d{4}$'
        if not re.match(pattern, phone):
            raise ValidationError("Phone number must be in format: '+999999999' or '999-999-9999'")


def validate_email_unique(email, exclude_id=None):
    query = Customer.objects.filter(email=email)
    if exclude_id:
        query = query.exclude(id=exclude_id)
    if query.exists():
        raise ValidationError("Email already exists")


# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    Output = CreateCustomerResponse

    def mutate(self, info, input):
        errors = []
        
        try:
            # Validate email uniqueness
            validate_email_unique(input.email)
            
            # Validate phone format
            if input.phone:
                validate_phone(input.phone)
            
            # Create customer
            customer = Customer.objects.create(
                name=input.name,
                email=input.email,
                phone=input.phone or None
            )
            
            return CreateCustomerResponse(
                customer=customer,
                message="Customer created successfully",
                success=True,
                errors=[]
            )
            
        except ValidationError as e:
            errors.extend(e.messages if hasattr(e, 'messages') else [str(e)])
        except Exception as e:
            errors.append(str(e))
        
        return CreateCustomerResponse(
            customer=None,
            message="Failed to create customer",
            success=False,
            errors=errors
        )


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    Output = BulkCreateCustomersResponse

    def mutate(self, info, input):
        customers = []
        errors = []
        
        with transaction.atomic():
            for i, customer_data in enumerate(input):
                try:
                    # Validate email uniqueness
                    validate_email_unique(customer_data.email)
                    
                    # Validate phone format
                    if customer_data.phone:
                        validate_phone(customer_data.phone)
                    
                    # Create customer
                    customer = Customer.objects.create(
                        name=customer_data.name,
                        email=customer_data.email,
                        phone=customer_data.phone or None
                    )
                    customers.append(customer)
                    
                except ValidationError as e:
                    error_msg = f"Customer {i+1}: {'; '.join(e.messages if hasattr(e, 'messages') else [str(e)])}"
                    errors.append(error_msg)
                except Exception as e:
                    errors.append(f"Customer {i+1}: {str(e)}")
        
        return BulkCreateCustomersResponse(
            customers=customers,
            errors=errors,
            success_count=len(customers),
            error_count=len(errors)
        )


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    Output = CreateProductResponse

    def mutate(self, info, input):
        errors = []
        
        try:
            # Validate price
            if input.price <= 0:
                raise ValidationError("Price must be positive")
            
            # Validate stock
            stock = input.stock if input.stock is not None else 0
            if stock < 0:
                raise ValidationError("Stock cannot be negative")
            
            # Create product
            product = Product.objects.create(
                name=input.name,
                price=input.price,
                stock=stock
            )
            
            return CreateProductResponse(
                product=product,
                message="Product created successfully",
                success=True,
                errors=[]
            )
            
        except ValidationError as e:
            errors.extend(e.messages if hasattr(e, 'messages') else [str(e)])
        except Exception as e:
            errors.append(str(e))
        
        return CreateProductResponse(
            product=None,
            message="Failed to create product",
            success=False,
            errors=errors
        )


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    Output = CreateOrderResponse

    def mutate(self, info, input):
        errors = []
        
        try:
            # Validate customer exists
            try:
                customer = Customer.objects.get(id=input.customer_id)
            except Customer.DoesNotExist:
                raise ValidationError("Invalid customer ID")
            
            # Validate products exist
            if not input.product_ids:
                raise ValidationError("At least one product must be selected")
            
            products = Product.objects.filter(id__in=input.product_ids)
            if len(products) != len(input.product_ids):
                raise ValidationError("One or more invalid product IDs")
            
            # Create order
            with transaction.atomic():
                order = Order.objects.create(
                    customer=customer,
                    order_date=input.order_date
                )
                
                # Add products to order
                order.products.set(products)
                
                # Calculate total amount
                total = sum(product.price for product in products)
                order.total_amount = total
                order.save()
            
            return CreateOrderResponse(
                order=order,
                message="Order created successfully",
                success=True,
                errors=[]
            )
            
        except ValidationError as e:
            errors.extend(e.messages if hasattr(e, 'messages') else [str(e)])
        except Exception as e:
            errors.append(str(e))
        
        return CreateOrderResponse(
            order=None,
            message="Failed to create order",
            success=False,
            errors=errors
        )


# Queries
class Query(graphene.ObjectType):
    hello = graphene.String()
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)
    
    customer = graphene.Field(CustomerType, id=graphene.ID())
    product = graphene.Field(ProductType, id=graphene.ID())
    order = graphene.Field(OrderType, id=graphene.ID())

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


# Mutations
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()