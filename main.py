# main.py
# This is our main server file, built with FastAPI as per the guide.

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import uvicorn
import os

# Import our models and agent
from models.a2a import JSONRPCRequest, JSONRPCResponse
from agents.content_agent import ContentAgent

# Load environment variables (.env file)
load_dotenv()

# Initialize our agent
agent = ContentAgent()

# Create the FastAPI app instance
app = FastAPI(
    title="Content Idea Agent A2A",
    description="An AI agent that generates content ideas based on news, compliant with the A2A protocol.",
    version="1.0.0",
)

# This is our main endpoint that Telex will call
@app.post("/agent/")
@app.post("/agent")
async def a2a_endpoint(request: Request):
    """Main A2A endpoint for our content agent."""
    try:
        body = await request.json()
        
        # 1. Validate the incoming request using our Pydantic models
        rpc_request = JSONRPCRequest(**body)

        # 2. Get the user's message from the request
        user_message = rpc_request.params.message
        
        # 3. Process the message with our agent's logic
        agent_response_message = agent.process_message(user_message)

        # 4. Build the final JSON-RPC response
        response = JSONRPCResponse(
            id=rpc_request.id,
            result=agent_response_message
        )
        # .model_dump() is the Pydantic way of converting the object to a dictionary
        return response.model_dump()

    except Exception as e:
        # If anything goes wrong, return a structured error
        request_id = body.get("id") if "body" in locals() else None
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32603, "message": "Internal error", "data": {"details": str(e)}},
            },
        )

@app.get("/health")
async def health_check():
    """A simple health check endpoint."""
    return {"status": "healthy", "agent": "ContentAgent"}

# This block allows us to run the server directly for testing
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)