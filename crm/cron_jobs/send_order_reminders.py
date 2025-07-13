#!/usr/bin/env python3

from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Setup GraphQL Client
transport = RequestsHTTPTransport(url="http://localhost:8000/graphql", verify=False)
client = Client(transport=transport, fetch_schema_from_transport=True)

# Query: Pending orders from the last 7 days
query = gql("""
{
  orders(filter: { orderDate_Gte: "%s" }) {
    id
    customer {
      email
    }
  }
}
""" % (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'))

response = client.execute(query)

# Log orders
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
with open('/tmp/order_reminders_log.txt', 'a') as f:
    for order in response["orders"]:
        f.write(f"{timestamp} - Order {order['id']}: {order['customer']['email']}\n")

print("Order reminders processed!")
