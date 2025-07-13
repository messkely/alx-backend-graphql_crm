#!/bin/bash

# Get current timestamp
timestamp=$(date '+%Y-%m-%d %H:%M:%S')

# Run Django shell command to delete inactive customers
deleted=$(python3 manage.py shell <<EOF
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer
one_year_ago = timezone.now() - timedelta(days=365)
qs = Customer.objects.annotate(num_orders=Count('orders')).filter(num_orders=0, created_at__lt=one_year_ago)
count = qs.count()
qs.delete()
print(count)
EOF
)

# Log to file
echo "$timestamp - Deleted $deleted inactive customers" >> /tmp/customer_cleanup_log.txt
