#!/bin/bash

# Set current directory to script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../.." || exit 1  # Go to project root

# Activate virtualenv if needed (optional)
# source venv/bin/activate

# Run Django shell command to delete customers
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

# Use conditional logic to verify deletion
if [ "$deleted" -ge 0 ]; then
    echo "$timestamp - Deleted $deleted inactive customers" >> /tmp/customer_cleanup_log.txt
else
    echo "$timestamp - Failed to delete customers" >> /tmp/customer_cleanup_log.txt
fi
