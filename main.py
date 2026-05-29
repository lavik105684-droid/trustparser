from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import asyncio

app = FastAPI(title="Pixel Office Orchestrator API", version="1.0.0")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATE_FILE = os.path.join("_core", "shared_memory", "workflow_state.json")
LOG_FILE = os.path.join("_core", "logs", "team_log.md")

class TaskUpdate(BaseModel):
    agent: str
    task: str
    status: str

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Send initial data immediately upon connection
        await self.send_initial_data(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_initial_data(self, websocket: WebSocket):
        try:
            state = {}
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    state = json.load(f)
            
            logs = ""
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    logs = f.read()

            await websocket.send_json({
                "type": "INITIAL",
                "state": state,
                "logs": logs
            })
        except Exception as e:
            print(f"Error sending initial WebSocket data: {e}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, listen for any client messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Helper to check files and broadcast updates
async def check_and_broadcast():
    last_state_mtime = 0.0
    last_log_mtime = 0.0
    
    while True:
        try:
            state_updated = False
            log_updated = False
            
            if os.path.exists(STATE_FILE):
                mtime = os.path.getmtime(STATE_FILE)
                if mtime > last_state_mtime:
                    last_state_mtime = mtime
                    state_updated = True
            
            if os.path.exists(LOG_FILE):
                mtime = os.path.getmtime(LOG_FILE)
                if mtime > last_log_mtime:
                    last_log_mtime = mtime
                    log_updated = True
            
            if state_updated or log_updated:
                # Read fresh data
                state = {}
                if os.path.exists(STATE_FILE):
                    with open(STATE_FILE, "r", encoding="utf-8") as f:
                        state = json.load(f)
                
                logs = ""
                if os.path.exists(LOG_FILE):
                    with open(LOG_FILE, "r", encoding="utf-8") as f:
                        logs = f.read()
                
                await manager.broadcast({
                    "type": "UPDATE",
                    "state": state,
                    "logs": logs
                })
        except Exception as e:
            print(f"Error in file watcher task: {e}")
            
        await asyncio.sleep(1.0) # Check files every 1 second

@app.on_event("startup")
async def startup_event():
    # Start the file watcher as a background task in FastAPI
    asyncio.create_task(check_and_broadcast())

@app.get("/api/state")
async def get_state():
    if not os.path.exists(STATE_FILE):
        raise HTTPException(status_code=404, detail="Shared memory state file not found.")
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/task")
async def update_task(update: TaskUpdate):
    if not os.path.exists(STATE_FILE):
        raise HTTPException(status_code=404, detail="Shared memory state file not found.")
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        
        # Find or update desk/agent task
        agent_found = False
        for desk, agent_name in state.get("desks_mapping", {}).items():
            if agent_name.lower() == update.agent.lower():
                agent_found = True
                break
        
        if not agent_found:
            raise HTTPException(status_code=400, detail=f"Agent '{update.agent}' not mapped to any desk.")

        # Update task list
        tasks = state.get("current_tasks", [])
        # Remove old task for this agent
        tasks = [t for t in tasks if t.get("agent").lower() != update.agent.lower()]
        tasks.append({
            "agent": update.agent,
            "task": update.task,
            "status": update.status
        })
        state["current_tasks"] = tasks

        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
            
        # The file watcher will automatically detect this write and broadcast immediately!
        return {"status": "success", "message": f"Task for '{update.agent}' updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs")
async def get_logs():
    if not os.path.exists(LOG_FILE):
        raise HTTPException(status_code=404, detail="Team log file not found.")
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return {"logs": f.read()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)