# Hasura MCP Server

A Model Context Protocol (MCP) server that provides tools for managing users, entitlements, and grants through a Hasura GraphQL API.

## Database Schema

The system includes three main tables:

1. **users** - Stores user information
2. **entitlements** - Stores permission definitions
3. **grants** - Many-to-many relationship between users and entitlements

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
# Copy the SQL file to the postgres container
docker compose exec postgres psql -U postgres -d hasura -f /docker-entrypoint-initdb.d/init.sql

# Or run it directly
docker compose exec postgres psql -U postgres -d hasura -c "$(cat init.sql)"
```

### 3. Configure Hasura

1. Open Hasura Console: http://localhost:8080
2. Use admin secret: `myadminsecretkey`
3. Go to Data tab and click "Track All" to track all tables
4. Go to Relationships tab and configure relationships if needed

### 4. Install MCP Server Dependencies

```bash
npm install
```

### 5. Start the MCP Server

```bash
npm start
```

## Available Tools

The MCP server provides the following tools:

- `get_users` - Get all users
- `get_user_entitlements` - Get entitlements for a specific user
- `get_entitlements` - Get all available entitlements
- `get_grants` - Get all grants (user-entitlement relationships)
- `create_user` - Create a new user
- `create_entitlement` - Create a new entitlement
- `grant_entitlement` - Grant an entitlement to a user
- `revoke_entitlement` - Revoke an entitlement from a user

## Sample Data

The system comes with sample data:

### Users
- Alice Johnson (alice@example.com)
- Bob Smith (bob@example.com)
- Charlie Brown (charlie@example.com)
- Diana Prince (diana@example.com)

### Entitlements
- Read Documents
- Write Documents
- Delete Documents
- Admin Access
- User Management
- Report Generation

### Grants
- Alice: Read and Write Documents
- Bob: Admin Access and User Management
- Charlie: Read Documents only
- Diana: Report Generation and Read Documents

## Usage with Claude

Once the MCP server is running, you can use it with Claude to:

1. Query user information and their entitlements
2. Create new users and entitlements
3. Grant or revoke permissions
4. Analyze access patterns and relationships

Example queries:
- "Show me all users and their entitlements"
- "Create a new user with email john@example.com"
- "Grant read access to user Charlie"
- "Who has admin access in the system?"

## Configuration

### Hasura Configuration
- Endpoint: `http://localhost:8080/v1/graphql`
- Admin Secret: `myadminsecretkey`

### Database Configuration
- Host: localhost
- Port: 5432
- Database: hasura
- Username: postgres
- Password: postgrespassword

## Development

For development, you can use:

```bash
npm run dev
```

This will start the server with auto-reload on file changes.