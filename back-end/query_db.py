# %% Import libraries
import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client
from pydantic import BaseModel, Field
from typing import Literal, Optional, Union
from openai import OpenAI
from langchain_core.tools import tool

from process_data.tables_metadata import METADATA

# %% Calling environment variables
load_dotenv(override=True)

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
openai_api_key = os.environ.get("OPENAI_API_KEY")

# %% Define structure
class FilterCondition(BaseModel):
    field: str = Field(description="Name of the field to filter by")
    operator: Literal[
        "eq", "neq", "gt", "gte", "lt", "lte", "like", "ilike", "in_"
    ] = Field(
        description=(
            "Comparison operator:\n"
            "- eq: Equal to\n"
            "- neq: Not equal to\n"
            "- gt: Greater than\n"
            "- gte: Greater than or equal to\n"
            "- lt: Less than\n"
            "- lte: Less than or equal to\n"
            "- like: Case-sensitive pattern matching / contains\n"
            "- ilike: Case-insensitive pattern matching / contains\n"
            "- in_: Value exists within a specified list of values"
        )
    )
    value: Union[str, int, float, bool, list[str], list[int]] = Field(description="Value to compare against")

class QuerySchema(BaseModel):
    table_name: str = Field(
        description="The name of the resulting data table or dataset."
    )
    fields: list[str] = Field(
        description="A list of columns/fields in the table."
    )
    filters: Optional[list[FilterCondition]] = Field(
        default=None, description="List of filter conditions (WHERE clause)"
    )
    order_by: Optional[str] = Field(
        default=None, description="Name of the field to sort by"
    )
    ascending: bool = Field(
        default=True, description="True for ascending order, False for descending"
    )
    limit: int = Field(
        default=10, description="Maximum number of records to return"
    )

class OutputData(BaseModel):
    queries: list[QuerySchema] = Field(
        default_factory=list,
        description="List of queries need to excute."
    )

# %% Excute query
supabase_client: Client = create_client(supabase_url, supabase_key)
openai_client = OpenAI(api_key=openai_api_key)

def get_instruction(table_metadata: list[dict]) -> str:
    """
    Generate an instruction prompt containing the database schema, 
    descriptions, and fields to help the agent infer the correct table and columns.
    """
    schema_lines = []
    
    for item in table_metadata:
        table_name = item["table_name"]
        table_desc = item["description"]
        
        schema_lines.append(f"- Table Name: {table_name}")
        schema_lines.append(f"  Description: {table_desc}")
        schema_lines.append("  Fields:")
        
        for field_name, field_info in item["fields"].items():
            field_desc = field_info.get("desc", "No description")
            field_public = field_info['public']
            schema_lines.append(f"    * {field_name} ({'Public' if field_public else 'Not Public'}): {field_desc}")
        
        schema_lines.append("#"*40)

    tables_info = "\n".join(schema_lines)
    
    system_prompt = f"""You are a database assistant. Your task is to analyze the user's request, infer which table(s) and fields should be queried, and invoke the appropriate tool.
Here is the database schema and metadata you can work with:
{tables_info}
Guidelines:
1. Choose the most relevant table based on the table descriptions.
2. Select the necessary fields.
3. **Security & Privacy Rule for 'Not Public' fields**:
   - Fields marked as **(Not Public)** are strictly for internal background processing, system logic, or hidden filtering only. They must **never** be exposed, displayed, or returned to the user.
   - Users are **not allowed** to query or access 'Not Public' fields.
   - **Crucial**: If the user's request explicitly attempts to query, access, or expose any 'Not Public' field, you **must immediately reject it** by returning an empty list for queries (`queries: []`).
    """
    return system_prompt

def get_query_schema(user_query: str, system_prompt: str):
    "Analyze the user's natural language request and generate structured query configurations \
    (table names, selected fields, and filters) to fetch data from the database."
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]
    response = openai_client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=messages,
        response_format=OutputData
    )
    result = response.choices[0].message.parsed
    return result.queries

def excute_query(query_spec: QuerySchema):
    "Execute a structured database query on Supabase using the provided query specification \
    (including table name, fields, filter conditions, sorting rules, and limits) and return the retrieved raw data."
    table_name = query_spec.table_name
    table_meta = next((t for t in METADATA if t['table_name'] == table_name), None)
    if not table_meta:
        return {"error": f"Table {table_name} does not exit or is not allowed."}

    query = supabase_client.table(table_name).select(
        ",".join(query_spec.fields)
    )

    if query_spec.filters:
        for filter in query_spec.filters:
            operator = filter.operator
            value = filter.value
            field = filter.field
            if operator == "in_":
                if not isinstance(value, list):
                    value = [value]
            elif operator == "ilike":
                value = f"%{value}%"

            if hasattr(query, operator):
                query = getattr(query, operator)(field, value)
            else:
                return {"error": f"Operator '{operator}' is not supported."}

    if query_spec.order_by:
        query = query.order(column=query_spec.order_by, desc=not query_spec.ascending)

    response = query.limit(query_spec.limit).execute()
    json_result_string = json.dumps(response.data, ensure_ascii=False, indent=2)
    return {table_name: json_result_string}

@tool
def get_data(user_input: str):
    "Analyze the user's natural language request, automatically generate appropriate database query specifications, \
    execute them across the database and return the retrieved data results."
    system_prompt = get_instruction(METADATA)
    queries_schema = get_query_schema(user_input, system_prompt)
    data = []

    for query in queries_schema:
        output = excute_query(query)
        data.append(output)
    return data

