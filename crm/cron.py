import requests
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    try:
        res = requests.post("http://localhost:8000/graphql", json={'query': '{ hello }'})
        status = "responsive" if res.status_code == 200 else "down"
    except Exception:
        status = "down"
    with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
        f.write(f"{timestamp} CRM is alive - Status: {status}\n")

def update_low_stock():
    client = Client(
        transport=RequestsHTTPTransport(url="http://localhost:8000/graphql", verify=False),
        fetch_schema_from_transport=True
    )

    mutation = gql("""
    mutation {
      updateLowStockProducts {
        success
        updated
      }
    }
    """)

    result = client.execute(mutation)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("/tmp/low_stock_updates_log.txt", "a") as f:
        for item in result["updateLowStockProducts"]["updated"]:
            f.write(f"{timestamp} - {item}\n")
