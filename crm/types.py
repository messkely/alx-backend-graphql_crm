import graphene
from graphene_django import DjangoObjectType
from graphene import relay

from ..models import Customer, Product, Order

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (relay.Node,)  # Required for DjangoFilterConnectionField
        fields = "__all__"          # Expose all fields

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (relay.Node,)
        fields = "__all__"

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (relay.Node,)
        fields = "__all__"
