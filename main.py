# main.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import uvicorn
import os

from models.a2a import JSONRPCRequest, JSONRPCResponse, TaskResult
from agents.content_agent import ContentAgent

load_dotenv()
agent = ContentAgent()
app = FastAPI(title="Content Idea Agent A2A", version="1.0.0")

@app.post("/agent/")
@app.post("/agent")
async def a2a_endpoint(request: Request):
    try:
        body = await request.json()
        rpc_request = JSONRPCRequest(**body)
        
        user_message = rpc_request.params.message
        task_id = rpc_request.params.taskId
        context_id = rpc_request.params.contextId
        
        # Process the message and get the full TaskResult
        task_result = agent.process_message(user_message, task_id, context_id)

        # Build the final JSON-RPC response
        response = JSONRPCResponse(id=rpc_request.id, result=task_result)
        return response.model_dump()

    except Exception as e:
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
    return {"status": "healthy", "agent": "ContentAgent"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)