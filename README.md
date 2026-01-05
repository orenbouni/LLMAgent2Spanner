# Spanner Logistics Agent

This project implements an intelligent multi-agent system capable of interacting with Google Cloud Spanner using both GoogleSQL and Graph Query Language (GQL). Built with the Google Agent Development Kit (ADK) and Vertex AI `gemini-3-pro-preview`, it features a routing agent that delegates tasks to specialized sub-agents.

## Agent Architecture

The system uses a hierarchical agent structure:
- **`spanner_router_agent`**: The main entry point. It analyzes user requests and routes them to the appropriate specialist.
- **`sql_agent`**: Handles standard data retrieval, aggregation, and list-based queries using Spanner's SQL interface.
- **`gql_agent`**: Handles requests related to graph visualization, path tracing, and relationship analysis using Spanner's Graph (GQL) capabilities.

## Prerequisites

- Python 3.11+
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (`gcloud`) installed and configured.
- Access to a Google Cloud Spanner instance and a Vertex AI-enabled project.

## Setup Instructions

### 1. Create and Activate Virtual Environment

Create a virtual environment to isolate dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Google Cloud Authentication

Authenticate with Google Cloud so the agent can access Spanner and Vertex AI:

```bash
# Set application default credentials (ADC)
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

### 4. Configuration

Create a `.env` file in the root directory (based on the provided template if available) with the following variables:

```env
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=your-region-id  # e.g., us-central1, me-west1
```

> **Configuration Note:** The Spanner instance ID and database ID are currently configured within the code at `agent/spanner_agnet/spanner_tools.py`. Please verify these match your environment.

## Running the Agent

To start the ADK web server and interact with the agent:

1. Navigate to the `agent` directory:
   ```bash
   cd agent
   ```

2. Start the web server:
   ```bash
   adk web
   ```

3. Open your browser to the URL shown (typically `http://localhost:8000`) to chat with the agent.

## Project Structure

- `agent/`: Contains the agent implementation.
  - `spanner_agnet/`: Main agent package (note: directory name currently contains a typo).
    - `agent.py`: Defines the main Router agent.
    - `sql_agent.py`: The SQL specialist agent.
    - `gql_agent.py`: The Graph/GQL specialist agent.
    - `spanner_tools.py`: Tools for interacting with Spanner.
- `requirements.txt`: Python dependencies.
