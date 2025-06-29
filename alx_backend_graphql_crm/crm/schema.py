import graphene
from graphene_django.types import DjangoObjectType
from .models import Customer, Product, Order
from django.utils import timezone
from django.core.exceptions import ValidationError
from graphql import GraphQLError