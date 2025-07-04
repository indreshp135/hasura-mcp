# Hasura MCP Server

A Model Context Protocol (MCP) server that provides tools for querying and managing data through a Hasura GraphQL API.

## Setup Instructions

### 1. Start Hasura and PostgreSQL

```bash
# Start the containers
docker compose up -d

# Wait for containers to be ready
docker compose logs -f
```

### 2. Initialize the Database

Connect to PostgreSQL and run the initialization script:

```bash
# Run the initialization script
docker compose exec postgres psql -U postgres -d hasura -f /docker-entrypoint-initdb.d/init.sql
```

### 3. Configure Hasura

1. Open Hasura Console: http://localhost:8080
2. Use admin secret: `myadminsecretkey`
3. Go to Data tab and click "Track All" to track all tables and relationships

### 4. Install MCP Server Dependencies

```bash
uv sync
```

### 5. Start the MCP Server

```bash
python server.py
```

## Available Tools

The MCP server provides the following tools:

- `query_graphql` - Execute any GraphQL query with optional variables
- `list_tables` - List all available tables in your Hasura schema
- `describe_table` - Get the schema/structure of a specific table
- `insert_data` - Insert data into a table using GraphQL mutation
- `update_data` - Update data in a table using GraphQL mutation  
- `delete_data` - Delete data from a table using GraphQL mutation

## Usage with Claude

Once the MCP server is running, you can use it with Claude to:

1. Query data from your Hasura database
2. Insert, update, and delete records
3. Explore table schemas and relationships
4. Execute complex GraphQL queries

Example queries:
- "Show me all the tables in the database"
- "What's the structure of the users table?"
- "Insert a new user with name 'John Doe' and email 'john@example.com'"
- "Query all users and their related data"

## Configuration

The MCP server connects to your Hasura GraphQL endpoint. Default configuration:

- **Hasura Endpoint**: `http://localhost:8080/v1/graphql`
- **Admin Secret**: `myadminsecretkey`

### Database Configuration (via Docker Compose)
- **Host**: localhost
- **Port**: 5432
- **Database**: hasura
- **Username**: postgres
- **Password**: postgrespassword

## Environment Variables

Set these environment variables before running the server:

```bash
export HASURA_ENDPOINT="http://localhost:8080/v1/graphql"
export HASURA_ADMIN_SECRET="myadminsecretkey"
```

Or create a `.env` file in the project root with:

```
HASURA_ENDPOINT=http://localhost:8080/v1/graphql
HASURA_ADMIN_SECRET=myadminsecretkey
```

## Development

To modify the server, edit `server.py` and restart:

```bash
python server.py
```

## Troubleshooting

### Common Issues

1. **Connection refused**: Make sure Hasura is running on the correct port
2. **Authentication error**: Check your admin secret
3. **GraphQL errors**: Verify your table names and schema in Hasura Console

### Logs

Check Docker logs for database and Hasura issues:

```bash
docker compose logs hasura
docker compose logs postgres
```