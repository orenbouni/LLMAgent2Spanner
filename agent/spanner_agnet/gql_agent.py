from google.adk.agents.llm_agent import LlmAgent
from .spanner_tools import run_graph_query_viz

gql_agent = LlmAgent(
    name="gql_agent",
    model="gemini-3-pro-preview",
    description="Specialized agent for running Graph queries on Spanner and visualizing the network.",
    instruction="""You are a Spanner Graph (GQL) expert.
    Your goal is to translate user questions into GQL queries and visualize them.
    
    ### Schema
    Graph: 'LogisticsGraph'
    Nodes: Warehouses, Customers, Products, Shipments
    Edges:
       - :DISPATCHED (Warehouses -> Shipments)
       - :DELIVERED_TO (Shipments -> Customers)
       - :INCLUDES (Shipments -> Products)
       
    ### Rules
    1. Use ISO GQL syntax (GRAPH LogisticsGraph MATCH ...).
    2. ALWAYS return nodes and edges as JSON objects using `TO_JSON(...)`.
       Example: `RETURN TO_JSON(s) AS s_node, TO_JSON(d) AS d_edge`
    3. Use the visualization tool to execute the query.
    """,
    tools=[run_graph_query_viz]
)
