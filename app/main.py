import sys
import os
import shutil
import logging
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to sys.path to allow importing agent
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

try:
    from agent.spanner_agnet.agent import root_agent
    from google.adk.runners import InMemoryRunner
except ImportError as e:
    logger.error(f"Failed to import agent or runner: {e}")
    root_agent = None

# Global runner instance
runner = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global runner
    if root_agent:
        logger.info("Initializing InMemoryRunner with root_agent")
        runner = InMemoryRunner(agent=root_agent)
    else:
        logger.warning("root_agent not loaded, chat endpoints will fail")
    yield
    # Cleanup if needed

app = FastAPI(lifespan=lifespan)

# create static directory if not exists
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_session"

@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            return f.read()
    return "<h1>Frontend not found. Please ensure app/static/index.html exists.</h1>"

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    global runner
    if not runner:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Using run_debug for simplicity as it handles message conversion and session management logic automatically
        logger.info(f"Processing message for session {request.session_id}: {request.message[:50]}...")
        events = await runner.run_debug(
            user_messages=request.message,
            session_id=request.session_id,
            verbose=True, # Need verbose to likely see tool calls? distinct events are always returned actually.
            quiet=True    # suppress console output
        )
        
        # Extract text from the last agent event
        response_text = ""
        has_visualization = False
        executed_queries = []
        
        # Analyze events
        for event in events:
            # Check for model text response
            if hasattr(event, 'content') and event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                         if hasattr(event.content, 'role') and event.content.role == 'model':
                             response_text += part.text
            
            # Check for tool execution (visualization and queries)
            if hasattr(event, 'content') and event.content and event.content.parts:
                for part in event.content.parts:
                     if hasattr(part, 'function_call') and part.function_call:
                         fc = part.function_call
                         # Detect visualization
                         if fc.name == 'run_graph_query_viz':
                             has_visualization = True
                         
                         # Extract Query if present
                         if fc.name in ['run_sql_query', 'run_graph_query_viz']:
                             # args is usually a dict-like object (Struct)
                             if hasattr(fc, 'args') and 'query' in fc.args:
                                 executed_queries.append({
                                     "tool": fc.name,
                                     "query": fc.args['query']
                                 })

        if not response_text:
             response_text = "No response from agent."

        visualization_url = None
        if has_visualization:
            # Check if local_example.html exists in root (project_root)
            source_path = os.path.join(project_root, "local_example.html")
            dest_path = os.path.join(static_dir, "local_example.html")
            
            if os.path.exists(source_path):
                # Move or Copy to static
                shutil.copy2(source_path, dest_path)
                visualization_url = "/static/local_example.html"
                logger.info("Visualization found and copied to static.")
            else:
                logger.warning(f"Visualization tool called but {source_path} not found.")

        return {
            "response": response_text,
            "visualization_url": visualization_url,
            "queries": executed_queries
        }

    except Exception as e:
        logger.error(f"Error during chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
