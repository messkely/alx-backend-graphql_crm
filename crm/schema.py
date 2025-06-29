from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
from .types import CustomerNode, ProductNode, OrderNode  # Assuming you used DjangoObjectType

class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerNode, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductNode, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderNode, filterset_class=OrderFilter)
