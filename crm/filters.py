import django_filters
from django.db import models
from ..models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    created_at = django_filters.DateFromToRangeFilter()
    created_at_gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at_lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    phone_pattern = django_filters.CharFilter(field_name='phone', lookup_expr='startswith')

    class Meta:
        model = Customer
        fields = ['name', 'email', 'created_at', 'phone_pattern']

    @property
    def qs(self):
        parent = super().qs
        return parent.order_by('name')


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    price = django_filters.RangeFilter()
    price_gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    stock = django_filters.NumberFilter()
    stock_gte = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock_lte = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')
    low_stock = django_filters.BooleanFilter(method='filter_low_stock')

    class Meta:
        model = Product
        fields = ['name', 'price', 'stock']

    def filter_low_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__lt=10)
        return queryset

    @property
    def qs(self):
        parent = super().qs
        return parent.order_by('name')


class OrderFilter(django_filters.FilterSet):
    total_amount = django_filters.RangeFilter()
    total_amount_gte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    total_amount_lte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    order_date = django_filters.DateFromToRangeFilter()
    order_date_gte = django_filters.DateFilter(field_name='order_date', lookup_expr='gte')
    order_date_lte = django_filters.DateFilter(field_name='order_date', lookup_expr='lte')
    customer_name = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    product_name = django_filters.CharFilter(field_name='products__name', lookup_expr='icontains')
    product_id = django_filters.NumberFilter(field_name='products__id')

    class Meta:
        model = Order
        fields = ['total_amount', 'order_date', 'customer_name', 'product_name', 'product_id']

    @property
    def qs(self):
        parent = super().qs
        return parent.distinct().order_by('-order_date')