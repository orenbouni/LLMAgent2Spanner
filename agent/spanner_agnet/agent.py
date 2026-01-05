from google.adk.agents.llm_agent import LlmAgent
from .sql_agent import sql_agent
from .gql_agent import gql_agent

import os
from dotenv import load_dotenv

# Load environment variables from the root of the project (2 levels up)
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(env_path)

root_agent = LlmAgent(
  name="spanner_router_agent",
  model="gemini-3-pro-preview",
  description="Main agent that routes user requests to either the SQL agent for data retrieval or the Graph agent for visualization.",
  instruction="""You are a routing agent for a Spanner Logistics Assistant.
  
  Your job is to classify the user's request and delegate it to the appropriate sub-agent:
  
  1. **Routing to `sql_agent`**:
     - Use this for questions asking for counts, aggregates, lists, specific record details, or "how many", "what is the sum", "list all".
     - Examples: "How many shipments are pending?", "List top 5 products".
     
  2. **Routing to `gql_agent`**:
     - Use this for questions asking for visualization, paths, relationships, network analysis, or "trace", "show me the path".
     - Examples: "Visualize the supply chain for Alice", "Trace the path of shipment 123".
     
  Simply delegate the task. Do not try to answer it yourself.
  """,
  sub_agents=[sql_agent, gql_agent]
)