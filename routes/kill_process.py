from fastapi import APIRouter, HTTPException
import requests
from models.processes_model import KillRequest

router = APIRouter()

@router.post("/TaskManager/kill_process")
def kill_process_endpoint(req: KillRequest):
    if req.IP:
        agent_ip = req.IP
        agent_port = 8100

    url = f"http://{agent_ip}:{agent_port}/kill"
    results = []
    
    for pid in req.pids:
        try:
            resp = requests.post(
                url, 
                json={"pid": pid, "api_key": "myTopSecretKey321!"}, 
                timeout=30
            )
            results.append({
                "pid": pid,
                "status": resp.status_code,
                "result": resp.json() if resp.content else {}
            })
        except requests.exceptions.Timeout:
            results.append({
                "pid": pid, 
                "status": "timeout", 
                "result": "Request timed out"
            })
        except requests.exceptions.ConnectionError:
            results.append({
                "pid": pid, 
                "status": "connection_error", 
                "result": f"Cannot connect to agent at {agent_ip}:{agent_port}"
            })
        except Exception as e:
            results.append({
                "pid": pid, 
                "status": "error", 
                "result": str(e)
            })
    
    return {"results": results}