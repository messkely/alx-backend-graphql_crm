# ALX Backend GraphQL CRM

A Django-based CRM system with GraphQL API for managing customers, products, and orders.

## Features

- **GraphQL API** with queries and mutations
- **Customer Management** with validation and bulk creation
- **Product Management** with price and stock tracking
- **Order Management** with automatic total calculation
- **Advanced Filtering** for all entities
- **Data Validation** with custom error handling

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Seed database with sample data
python seed_db.py
```

### 3. Run the Server

```bash
python manage.py runserver
```

### 4. Access GraphQL Interface

Visit: `http://localhost:8000/graphql/`

## GraphQL Examples

### Basic Query

```graphql
{
  hello
}
```

### Customer Queries

```graphql
# Get all customers
{
  allCustomers {
    edges {
      node {
        id
        name
        email
        phone
        createdAt
      }
    }
  }
}

# Filter customers by name
{
  allCustomers(name_Icontains: "Alice") {
    edges {
      node {
        id
        name
        email
      }
    }
  }
}

# Filter customers by creation date
{
  allCustomers(createdAtGte: "2025-01-01") {
    edges {
      node {
        id
        name
        email
        createdAt
      }
    }
  }
}
```

### Product Queries

```graphql
# Get products with price filter
{
  allProducts(priceGte: 100, priceLte: 1000) {
    edges {
      node {
        id
        name
        price
        stock
      }
    }
  }
}

# Get low stock products
{
  allProducts(lowStock: true) {
    edges {
      node {
        id
        name
        stock
      }
    }
  }
}
```

### Order Queries

```graphql
# Get orders with customer and product details
{
  allOrders {
    edges {
      node {
        id
        customer {
          name
          email
        }
        products {
          edges {
            node {
              name
              price
            }
          }
        }
        totalAmount
        orderDate
      }
    }
  }
}

# Filter orders by customer name
{
  allOrders(customerName: "Alice") {
    edges {
      node {
        id
        customer {
          name
        }
        totalAmount
      }
    }
  }
}
```

### Mutations

#### Create Customer

```graphql
mutation {
  createCustomer(input: {
    name: "Alice",
    email: "alice@example.com",
    phone: "+1234567890"
  }) {
    customer {
      id
      name
      email
      phone
    }
    message
    success
    errors
  }
}
```

#### Bulk Create Customers

```graphql
mutation {
  bulkCreateCustomers(input: [
    { name: "Bob", email: "bob@example.com", phone: "123-456-7890" },
    { name: "Carol", email: "carol@example.com" }
  ]) {
    customers {
      id
      name
      email
    }
    errors
    successCount
    errorCount
  }
}
```

#### Create Product

```graphql
mutation {
  createProduct(input: {
    name: "Laptop",
    price: 999.99,
    stock: 10
  }) {
    product {
      id
      name
      price
      stock
    }
    message
    success
    errors
  }
}
```

#### Create Order

```graphql
mutation {
  createOrder(input: {
    customerId: "1",
    productIds: ["1", "2"]
  }) {
    order {
      id
      customer {
        name
      }
      products {
        edges {
          node {
            name
            price
          }
        }
      }
      totalAmount
      orderDate
    }
    message
    success
    errors
  }
}
```

## Advanced Filtering Examples

### Customer Filtering

```graphql
# Filter by phone pattern (starts with +1)
{
  allCustomers(phonePattern: "+1") {
    edges {
      node {
        name
        phone
      }
    }
  }
}

# Filter by date range
{
  allCustomers(createdAtGte: "2025-01-01", createdAtLte: "2025-12-31") {
    edges {
      node {
        name
        createdAt
      }
    }
  }
}
```

### Product Filtering

```graphql
# Filter by stock range
{
  allProducts(stockGte: 5, stockLte: 20) {
    edges {
      node {
        name
        stock
      }
    }
  }
}

# Filter by name and price
{
  allProducts(name_Icontains: "Laptop", priceGte: 500) {
    edges {
      node {
        name
        price
      }
    }
  }
}
```

### Order Filtering

```graphql
# Filter by total amount range
{
  allOrders(totalAmountGte: 100, totalAmountLte: 1000) {
    edges {
      node {
        id
        totalAmount
        customer {
          name
        }
      }
    }
  }
}

# Filter by product name
{
  allOrders(productName: "Laptop") {
    edges {
      node {
        id
        customer {
          name
        }
        products {
          edges {
            node {
              name
            }
          }
        }
      }
    }
  }
}

# Filter by specific product ID
{
  allOrders(productId: 1) {
    edges {
      node {
        id
        customer {
          name
        }
        totalAmount
      }
    }
  }
}
```

## Project Structure

```
alx-backend-graphql_crm/
├── alx_backend_graphql_crm/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── crm/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── filters.py
│   ├── models.py
│   ├── schema.py
│   └── migrations/
├── schema.py
├── seed_db.py
├── requirements.txt
└── manage.py
```

## Key Features Implemented

### Task 0: GraphQL Endpoint Setup
- ✅ Basic GraphQL endpoint with "Hello, GraphQL!" query
- ✅ GraphiQL interface enabled

### Task 1: CRM Database Models
- ✅ Customer model with validation
- ✅ Product model with price and stock
- ✅ Order model with many-to-many product relationships
- ✅ Automatic total amount calculation

### Task 2: GraphQL Mutations
- ✅ CreateCustomer with email uniqueness validation
- ✅ BulkCreateCustomers with partial success support
- ✅ CreateProduct with price/stock validation
- ✅ CreateOrder with relationship validation
- ✅ Comprehensive error handling

### Task 3: Advanced Filtering
- ✅ Customer filtering by name, email, date, phone pattern
- ✅ Product filtering by name, price range, stock range, low stock
- ✅ Order filtering by amount, date, customer name, product name
- ✅ Related field lookups and distinct results

## Validation Rules

### Customer Validation
- Email must be unique
- Phone format: `+1234567890` or `123-456-7890`

### Product Validation
- Price must be positive
- Stock cannot be negative

### Order Validation
- Customer must exist
- At least one product must be selected
- All product IDs must be valid
- Total amount calculated automatically

## Error Handling

The API provides detailed error messages for:
- Validation failures
- Duplicate entries
- Missing required fields
- Invalid references
- Database constraints

## Testing

Use the GraphiQL interface at `http://localhost:8000/graphql/` to test all queries and mutations. The interface provides:
- Schema documentation
- Query autocompletion
- Real-time error feedback
- Query history

## Troubleshooting

### Common Issues

1. **Migration errors**: Ensure you run `makemigrations` before `migrate`
2. **Import errors**: Check that all apps are added to `INSTALLED_APPS`
3. **GraphQL schema errors**: Verify all imports in schema files
4. **Validation errors**: Check that required fields are provided in mutations

### Debug Mode

Set `DEBUG = True` in settings.py for detailed error messages during development.