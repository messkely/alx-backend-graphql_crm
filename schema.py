import django_filters
from django.db.models import Q
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', help_text="Filter by name (case-insensitive partial match)")
    email = django_filters.CharFilter(lookup_expr='icontains', help_text="Filter by email (case-insensitive partial match)")
    created_at_gte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte', help_text="Filter customers created after this date")
    created_at_lte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte', help_text="Filter customers created before this date")
    phone_pattern = django_filters.CharFilter(method='filter_phone_pattern', help_text="Filter by phone number pattern (e.g., starts with +1)")

    class Meta:
        model = Customer
        fields = ['name', 'email']

    def filter_phone_pattern(self, queryset, name, value):
        """Custom filter for phone number patterns"""
        if value:
            return queryset.filter(phone__icontains=value)
        return queryset


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', help_text="Filter by product name (case-insensitive partial match)")
    price_gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte', help_text="Filter products with price greater than or equal to")
    price_lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte', help_text="Filter products with price less than or equal to")
    stock_gte = django_filters.NumberFilter(field_name='stock', lookup_expr='gte', help_text="Filter products with stock greater than or equal to")
    stock_lte = django_filters.NumberFilter(field_name='stock', lookup_expr='lte', help_text="Filter products with stock less than or equal to")
    low_stock = django_filters.BooleanFilter(method='filter_low_stock', help_text="Filter products with low stock (less than 10)")

    class Meta:
        model = Product
        fields = ['name', 'price', 'stock']

    def filter_low_stock(self, queryset, name, value):
        """Filter products with low stock (< 10)"""
        if value:
            return queryset.filter(stock__lt=10)
        return queryset


class OrderFilter(django_filters.FilterSet):
    total_amount_gte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte', help_text="Filter orders with total amount greater than or equal to")
    total_amount_lte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte', help_text="Filter orders with total amount less than or equal to")
    order_date_gte = django_filters.DateTimeFilter(field_name='order_date', lookup_expr='gte', help_text="Filter orders placed after this date")
    order_date_lte = django_filters.DateTimeFilter(field_name='order_date', lookup_expr='lte', help_text="Filter orders placed before this date")
    customer_name = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains', help_text="Filter orders by customer name")
    product_name = django_filters.CharFilter(method='filter_by_product_name', help_text="Filter orders containing products with this name")
    product_id = django_filters.NumberFilter(method='filter_by_product_id', help_text="Filter orders containing a specific product ID")

    class Meta:
        model = Order
        fields = ['total_amount', 'order_date']

    def filter_by_product_name(self, queryset, name, value):
        """Filter orders by product name (case-insensitive partial match)"""
        if value:
            return queryset.filter(products__name__icontains=value).distinct()
        return queryset

    def filter_by_product_id(self, queryset, name, value):
        """Filter orders containing a specific product ID"""
        if value:
            return queryset.filter(products__id=value).distinct()
        return queryset