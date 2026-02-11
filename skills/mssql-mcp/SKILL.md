---
name: mssql-mcp
description: SQL Server database interaction using mssql-mcp server. This skill enables querying, inserting, updating, and managing SQL Server databases through natural language. Use when you need to work with SQL Server databases for tasks like querying data, managing tables, or performing CRUD operations.
---

# mssql-mcp Skill

This skill provides an interface for interacting with SQL Server databases using the mssql-mcp server. It enables natural language interaction with SQL Server databases, allowing you to query, insert, update, and manage data without writing raw SQL queries.

## Prerequisites

- mssql-mcp server must be configured in Claude Code
- SQL Server instance must be accessible
- Valid authentication credentials must be configured (either SQL Server authentication or Azure Active Directory authentication)

## Available Tools

### 1. list_table
Lists all tables in the database.

#### Usage:
```json
{
  "method": "tools/call",
  "params": {
    "name": "list_table",
    "arguments": {}
  }
}
```

#### Example Response:
```json
{
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"success\": true, \"message\": \"List tables executed successfully\", \"items\": [{\"\": \"dbo.Table1\"}, {\"\": \"dbo.Table2\"}, ...]}"
      }
    ]
  },
  "jsonrpc": "2.0",
  "id": "1"
}
```

### 2. read_data
Executes a SELECT query on a table.

#### Usage:
```json
{
  "method": "tools/call",
  "params": {
    "name": "read_data",
    "arguments": {
      "query": "SELECT * FROM table_name WHERE condition"
    }
  }
}
```

#### Example:
```json
{
  "method": "tools/call",
  "params": {
    "name": "read_data",
    "arguments": {
      "query": "SELECT TOP 10 * FROM dbo.T_CINS_dwell"
    }
  }
}
```

### 3. describe_table
Describes the schema of a specific table.

#### Usage:
```json
{
  "method": "tools/call",
  "params": {
    "name": "describe_table",
    "arguments": {
      "tableName": "table_name"
    }
  }
}
```

#### Example:
```json
{
  "method": "tools/call",
  "params": {
    "name": "describe_table",
    "arguments": {
      "tableName": "T_CINS_dwell"
    }
  }
}
```

### 4. insert_data
Inserts data into a table.

#### Usage:
```json
{
  "method": "tools/call",
  "params": {
    "name": "insert_data",
    "arguments": {
      "tableName": "table_name",
      "data": {
        "column1": "value1",
        "column2": "value2"
      }
    }
  }
}
```

#### Example (Single Record):
```json
{
  "method": "tools/call",
  "params": {
    "name": "insert_data",
    "arguments": {
      "tableName": "Users",
      "data": {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30
      }
    }
  }
}
```

#### Example (Multiple Records):
```json
{
  "method": "tools/call",
  "params": {
    "name": "insert_data",
    "arguments": {
      "tableName": "Users",
      "data": [
        {
          "name": "John Doe",
          "email": "john@example.com",
          "age": 30
        },
        {
          "name": "Jane Smith",
          "email": "jane@example.com",
          "age": 25
        }
      ]
    }
  }
}
```

### 5. update_data
Updates data in a table with a WHERE clause.

#### Usage:
```json
{
  "method": "tools/call",
  "params": {
    "name": "update_data",
    "arguments": {
      "tableName": "table_name",
      "updates": {
        "column1": "new_value1",
        "column2": "new_value2"
      },
      "whereClause": "condition"
    }
  }
}
```

#### Example:
```json
{
  "method": "tools/call",
  "params": {
    "name": "update_data",
    "arguments": {
      "tableName": "Users",
      "updates": {
        "email": "john.doe@example.com"
      },
      "whereClause": "name = 'John Doe'"
    }
  }
}
```

### 6. create_table
Creates a new table.

#### Usage:
```json
{
  "method": "tools/call",
  "params": {
    "name": "create_table",
    "arguments": {
      "tableName": "table_name",
      "columns": [
        {
          "name": "column1",
          "type": "data_type constraints"
        },
        {
          "name": "column2",
          "type": "data_type constraints"
        }
      ]
    }
  }
}
```

#### Example:
```json
{
  "method": "tools/call",
  "params": {
    "name": "create_table",
    "arguments": {
      "tableName": "Products",
      "columns": [
        {
          "name": "id",
          "type": "INT PRIMARY KEY"
        },
        {
          "name": "name",
          "type": "NVARCHAR(255) NOT NULL"
        },
        {
          "name": "price",
          "type": "DECIMAL(10, 2)"
        },
        {
          "name": "createdDate",
          "type": "DATETIME DEFAULT GETDATE()"
        }
      ]
    }
  }
}
```

### 7. drop_table
Drops a table from the database.

#### Usage:
```json
{
  "method": "tools/call",
  "params": {
    "name": "drop_table",
    "arguments": {
      "tableName": "table_name"
    }
  }
}
```

#### Example:
```json
{
  "method": "tools/call",
  "params": {
    "name": "drop_table",
    "arguments": {
      "tableName": "temp_table"
    }
  }
}
```

### 8. create_index
Creates an index on a table.

#### Usage:
```json
{
  "method": "tools/call",
  "params": {
    "name": "create_index",
    "arguments": {
      "tableName": "table_name",
      "indexName": "index_name",
      "columns": ["column1", "column2"],
      "isUnique": false,
      "isClustered": false
    }
  }
}
```

#### Example:
```json
{
  "method": "tools/call",
  "params": {
    "name": "create_index",
    "arguments": {
      "tableName": "Users",
      "indexName": "idx_users_email",
      "columns": ["email"],
      "isUnique": true,
      "isClustered": false
    }
  }
}
```

## Example Workflows

### 1. List All Tables
```bash
claude mcp call mssql-mcp list_table
```

### 2. Query Top 10 Records from a Table
```bash
claude mcp call mssql-mcp read_data --query "SELECT TOP 10 * FROM dbo.T_CINS_dwell"
```

### 3. Describe a Table Schema
```bash
claude mcp call mssql-mcp describe_table --tableName "T_CINS_dwell"
```

## Configuration

The mssql-mcp server is configured in `~/.claude.json` with the following environment variables:
- `SERVER_NAME`: SQL Server hostname or IP address
- `DATABASE_NAME`: Database name
- `SQL_USER`: SQL Server username (for SQL Server authentication)
- `SQL_PASSWORD`: SQL Server password (for SQL Server authentication)
- `TRUST_SERVER_CERTIFICATE`: Set to "true" to trust self-signed certificates
- `READONLY`: Set to "true" to restrict to read-only operations

## Troubleshooting

1. **Connection Issues**: Verify that the SQL Server instance is accessible and the credentials are correct
2. **Authentication Errors**: Check if the authentication method (SQL Server or Azure Active Directory) matches the configuration
3. **Permission Errors**: Ensure the user has the appropriate permissions for the requested operation
4. **Query Validation Errors**: Make sure read queries start with SELECT and do not contain dangerous keywords