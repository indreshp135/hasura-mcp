import json
import os
from typing import Any, Dict, Optional
import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP(
    "Grants Database MCP Server",
    instructions="""
This server interfaces with a Hasura GraphQL backend containing large data.
To ensure optimal performance and prevent issues with LLM context limits:
-> Avoid running broad queries that fetch all data or unnecessary fields.
-> Request only the specific fields and records you need.

When adding or updating data:
-> Provide all required fields explicitly—do not rely on assumed defaults
    or placeholders.
-> Follow the defined table schema carefully.
-> If you're unsure about the structure or requirements, ask for help
    and confirm before proceeding.
""",
)

HASURA_ENDPOINT = os.getenv("HASURA_ENDPOINT",
                            "http://localhost:8080/v1/graphql")
HASURA_ADMIN_SECRET = os.getenv("HASURA_ADMIN_SECRET", "myadminsecretkey")


class GraphQLQuery(BaseModel):
    """GraphQLQuery model for defining a GraphQL query.

    Args:
        BaseModel (_type_): Base model for Pydantic validation.
    """

    query: str = Field(
        description="GraphQL query string \
        (query, mutation, or subscription)"
    )
    variables: Optional[Dict[str, Any]] = None


async def execute_graphql_query(
    query: str, variables: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Execute a GraphQL query against the Hasura endpoint.

    Args:
        query (str): GraphQL query string (query, mutation, or subscription)
        variables (Optional[Dict[str, Any]], optional):
            Optional dictionary of variables. Defaults to None.

    Returns:
        Dict[str, Any]: JSON response from the GraphQL endpoint.
    """
    headers = {"Content-Type": "application/json"}
    if HASURA_ADMIN_SECRET:
        headers["X-Hasura-Admin-Secret"] = HASURA_ADMIN_SECRET

    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    async with httpx.AsyncClient() as client:
        response = await client.post(
            HASURA_ENDPOINT, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def query_graphql(query: str, variables: Optional[str] = None) -> str:
    """Execute any GraphQL query or mutation against Hasura.

    Args:
        query: GraphQL query string (query, mutation, or subscription)
        variables: Optional JSON string of variables (e.g., '{"id": 1}')

    Returns:
        JSON response from GraphQL endpoint

    Example:
        query = 'query { users { id name email } }'
        variables = '{"id": 1}'
    """
    try:
        parsed_variables = None
        if variables:
            parsed_variables = json.loads(variables)
        print(f"Executing query: {query} with variables: {parsed_variables}")
        result = await execute_graphql_query(query, parsed_variables)
        return json.dumps(result, indent=2)
    except json.JSONDecodeError as e:
        return f"Error parsing variables JSON: {str(e)}"
    except httpx.RequestError as e:
        return f"Error connecting to Hasura: {str(e)}"
    except httpx.HTTPStatusError as e:
        return f"HTTP error from Hasura:\
            {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Unexpected error executing GraphQL query: {str(e)}"


@mcp.tool()
async def list_tables() -> str:
    """List all tables available in the Hasura schema.

    Uses GraphQL introspection to discover queryable tables. Use this first
    to explore your database structure.

    Returns:
        JSON response with table names and types
    """
    query = """
    query {
        __schema {
            queryType {
                fields {
                    name
                    type {
                        name
                        kind
                    }
                }
            }
        }
    }
    """
    try:
        result = await execute_graphql_query(query)
        return json.dumps(result, indent=2)
    except httpx.RequestError as e:
        return f"Error connecting to Hasura: {str(e)}"
    except httpx.HTTPStatusError as e:
        return f"HTTP error from Hasura:\
            {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Unexpected error listing tables: {str(e)}"


@mcp.tool()
async def describe_table(table_name: str) -> str:
    """Get the schema/structure of a specific table.

    Uses GraphQL introspection to get field names, types, and relationships.
    Use this before performing queries or mutations on a table.

    Args:
        table_name: Name of the table to describe (e.g., "users", "posts")

    Returns:
        JSON response with table schema information
    """
    query = f"""
    query {{
        __type(name: "{table_name}") {{
            name
            fields {{
                name
                type {{
                    name
                    kind
                    ofType {{
                        name
                        kind
                    }}
                }}
            }}
        }}
    }}
    """
    try:
        result = await execute_graphql_query(query)
        return json.dumps(result, indent=2)
    except httpx.RequestError as e:
        return f"Error connecting to Hasura: {str(e)}"
    except httpx.HTTPStatusError as e:
        return f"HTTP error from Hasura:\
            {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Unexpected error describing table {table_name}: {str(e)}"

if __name__ == "__main__":
    mcp.run()
