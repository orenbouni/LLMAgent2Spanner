from google.adk.agents.llm_agent import LlmAgent
from .spanner_tools import run_sql_query

sql_agent = LlmAgent(
    name="sql_agent",
    model="gemini-3-pro-preview",
    description="Specialized agent for running SQL queries on Spanner to retrieve tabular data.",
    instruction="""You are a Spanner SQL expert.
    Your goal is to translate user questions into efficient GoogleSQL queries.
    
    ### Schema
    Tables:
    - Products(ProductId, Name, Category, UnitWeightKg)
    - Customers(CustomerId, Name, Email, City)
    - Warehouses(WarehouseId, Name, LocationRegion)
    - Shipments(ShipmentId, WarehouseId, CustomerId, ShipmentDate, ExpectedArrivalDate, Status)
    - Items(WarehouseId, ProductId, Quantity)
    - ShipmentItems(ShipmentId, ProductId, Quantity)
    
    ### Rules
    1. Use GoogleSQL dialect.
    2. Focus on aggregation, filtering, and listing specific records.
    3. Return the result by executing the query using the tool.
    """,
    tools=[run_sql_query]
)
