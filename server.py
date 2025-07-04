import json
import os
from typing import Any, Dict, Optional
import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

mcp = FastMCP("Hasura GraphQL MCP Server")

HASURA_ENDPOINT = os.getenv(
    "HASURA_ENDPOINT", "http://localhost:8080/v1/graphql")
HASURA_ADMIN_SECRET = os.getenv("HASURA_ADMIN_SECRET", "myadminsecretkey")


class GraphQLQuery(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """

    query: str
    variables: Optional[Dict[str, Any]] = None


async def execute_graphql_query(
    query: str, variables: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
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
    """Execute a GraphQL query against the Hasura endpoint.

    Args:
        query: The GraphQL query string
        variables: Optional JSON string of variables for the query

    Returns:
        JSON response from the GraphQL endpoint
    """
    try:
        parsed_variables = None
        if variables:
            parsed_variables = json.loads(variables)
        print(f"Executing query: {query} with variables: {parsed_variables}")
        result = await execute_graphql_query(query, parsed_variables)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error executing GraphQL query: {str(e)}"


@mcp.tool()
async def list_tables() -> str:
    """List all tables available in the Hasura schema."""
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
    except Exception as e:
        return f"Error listing tables: {str(e)}"


@mcp.tool()
async def describe_table(table_name: str) -> str:
    """Get the schema/structure of a specific table.

    Args:
        table_name: Name of the table to describe

    Returns:
        Table schema information
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
    except Exception as e:
        return f"Error describing table {table_name}: {str(e)}"


@mcp.tool()
async def insert_data(table_name: str, data: str) -> str:
    """Insert data into a table using GraphQL mutation.

    Args:
        table_name: Name of the table to insert into
        data: JSON string containing the data to insert

    Returns:
        Result of the insertion operation
    """
    try:
        parsed_data = json.loads(data)

        mutation = f"""
        mutation {{
            insert_{table_name}(objects: [{json.dumps(parsed_data)}]) {{
                affected_rows
                returning {{
                    id
                }}
            }}
        }}
        """

        result = await execute_graphql_query(mutation)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error inserting data into {table_name}: {str(e)}"


@mcp.tool()
async def update_data(table_name: str,
                      where_clause: str, set_data: str) -> str:
    """Update data in a table using GraphQL mutation.

    Args:
        table_name: Name of the table to update
        where_clause: JSON string for the where condition
        set_data: JSON string containing the data to update

    Returns:
        Result of the update operation
    """
    try:
        parsed_where = json.loads(where_clause)
        parsed_set = json.loads(set_data)

        mutation = f"""
        mutation {{
            update_{table_name}(
                where: {json.dumps(parsed_where)},
                _set: {json.dumps(parsed_set)}
            ) {{
                affected_rows
                returning {{
                    id
                }}
            }}
        }}
        """

        result = await execute_graphql_query(mutation)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error updating data in {table_name}: {str(e)}"


@mcp.tool()
async def delete_data(table_name: str, where_clause: str) -> str:
    """Delete data from a table using GraphQL mutation.

    Args:
        table_name: Name of the table to delete from
        where_clause: JSON string for the where condition

    Returns:
        Result of the deletion operation
    """
    try:
        parsed_where = json.loads(where_clause)

        mutation = f"""
        mutation {{
            delete_{table_name}(where: {json.dumps(parsed_where)}) {{
                affected_rowsƒ
            }}
        }}
        """

        result = await execute_graphql_query(mutation)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error deleting data from {table_name}: {str(e)}"


if __name__ == "__main__":
    mcp.run()
