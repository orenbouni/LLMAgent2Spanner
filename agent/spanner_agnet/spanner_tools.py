import os
import json
import uuid
import networkx as nx
from google.cloud import spanner
from typing import List, Dict, Any, Union
from ipysigma import Sigma
from google.adk.tools.tool_context import ToolContext

# --- Helper to get DB client ---
def get_spanner_database():
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    instance_id = "tlvinst" # Hardcoded per user context
    database_id = "tlvlog"  # Hardcoded per user context

    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set")

    spanner_client = spanner.Client(project=project_id)
    instance = spanner_client.instance(instance_id)
    database = instance.database(database_id)
    return database

# --- SQL Tool ---
def run_sql_query(tool_context: ToolContext, query: str) -> List[Dict[str, Any]]:
  """
  Executes a standard GoogleSQL query on Spanner and returns the results.
  Suitable for aggregation, filtering, and tabular data.
  
  Args:
      query (str): The SQL query string.
  
  Returns:
      List[Dict[str, Any]]: A list of rows associated with column names.
  """
  database = get_spanner_database()
  results = []
  
  with database.snapshot() as snapshot:
      result_set = snapshot.execute_sql(query)
      for row in result_set:
          row_dict = {}
          for i, field in enumerate(result_set.fields):
              row_dict[field.name] = row[i]
          results.append(row_dict)

  return results

# --- Graph Visualization Tool ---
def run_graph_query_viz(tool_context: ToolContext, query: str) -> str:
    """
    Executes a Spanner Graph (GQL) query and generates an interactive graph visualization.
    
    Args:
        query (str): The GQL query. MUST return nodes and edges using TO_JSON(...) aliased.
                     Example: RETURN TO_JSON(n) AS n_node, TO_JSON(e) AS e_edge

    Returns:
        str: HTML string or path to the visualization file.
    """
    database = get_spanner_database()
    results = []
    
    with database.snapshot() as snapshot:
        result_set = snapshot.execute_sql(query)
        for row in result_set:
            row_dict = {}
            for i, field in enumerate(result_set.fields):
                row_dict[field.name] = row[i]
            results.append(row_dict)
    
    # Build NetworkX Graph
    G = nx.MultiDiGraph()
    
    for row in results:
        for key, value in row.items():
            if not isinstance(value, dict):
                # Try parsing if string? Spanner python client usually parses JSON/STRUCT to dict/list
                continue
            
            element = value
            # Basic Graph element detection
            if 'identifier' in element:
                if 'source_node_identifier' in element:
                    # Edge
                    edge_id = str(element.get('identifier'))
                    source_id = str(element.get('source_node_identifier'))
                    target_id = str(element.get('destination_node_identifier'))
                    labels = element.get('labels', [])
                    rel_type = labels[0] if labels else 'RELATED'
                    props = element.get('properties', {})
                    G.add_edge(source_id, target_id, key=edge_id, label=rel_type, **props)
                else:
                    # Node
                    node_id = str(element.get('identifier'))
                    labels = element.get('labels', [])
                    category = labels[0] if labels else 'Unknown'
                    props = element.get('properties', {})
                    label_prop = props.get('Name', node_id)
                    G.add_node(node_id, label=label_prop, category=category, **props)

    if G.number_of_nodes() == 0:
        return f"Query returned {len(results)} rows but no graph elements could be parsed. Raw Results: {results[:2]}"

    # Visualization
    # Create valid directory for visualizations
    viz_dir = os.path.join(os.path.dirname(__file__), 'visualizations')
    os.makedirs(viz_dir, exist_ok=True)
    
    # Generate unique filename
    filename = f"graph_{uuid.uuid4().hex[:8]}.html"
    output_path = os.path.join(viz_dir, filename)
    
    # ipysigma save
    # Note: node_color, node_label, etc help style the graph
    test = Sigma.write_html(G, node_color="category", node_label="label", edge_label="label", height=600, path='./local_example.html')
    #TODO: return the html path and visualize it in the UI
    # Return a relative path or a message
    # If the user is running `adk web`, we might want to return the absolute path or a link if we served it.
    # For now, return the path.
    return f"Graph visualization generated at: {output_path}"
