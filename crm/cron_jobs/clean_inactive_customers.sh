#!/bin/bash

# Get current working directory of the script (cwd = current working directory)
cwd="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$cwd/../.." || exit 1  # Navigate to Django project root

# Run cleanup via Django shell
deleted=$(python3 manage.py shell <<EOF
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer
from django.db.models import Count

cutoff = timezone.now() - timedelta(days=365)
qs = Customer.objects.annotate(order_count=Count('orders')).filter(order_count=0, created_at__lt=cutoff)
count = qs.count()
qs.delete()
print(count)
EOF
)

# Logging
timestamp=$(date '+%Y-%m-%d %H:%M:%S')

# Check and log result
if [ "$deleted" -ge 0 ]; then
    echo "$timestamp - Deleted $deleted inactive customers" >> /tmp/customer_cleanup_log.txt
else
    echo "$timestamp - Failed to delete customers" >> /tmp/customer_cleanup_log.txt
fi
