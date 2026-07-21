import asyncio
import httpx
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from models.processes_model import KillRequest

router = APIRouter()
logger = logging.getLogger(__name__)

async def kill_single_pid(client: httpx.AsyncClient, url: str, pid: int, api_key: str):
    """Helper to kill a single PID asynchronously with error handling."""
    try:
        logger.info(f"Sending kill request for PID {pid} to {url}")
        resp = await client.post(
            url, 
            json={"pid": pid, "api_key": api_key}, 
            timeout=30.0
        )
        
        # Safe JSON decoding
        try:
            resp_data = resp.json() if resp.content else {}
        except ValueError:
            resp_data = {"raw_content": resp.text or "No content"}
            logger.warning(f"Agent returned non-JSON response for PID {pid}: {resp.status_code}")

        if resp.status_code >= 400:
            logger.error(f"Agent failed to kill PID {pid}. Status: {resp.status_code}, Body: {resp_data}")

        return {
            "pid": pid,
            "status": resp.status_code,
            "result": resp_data
        }

    except httpx.TimeoutException:
        logger.error(f"Timeout occurred while killing PID {pid} at {url}")
        return {
            "pid": pid, 
            "status": 504, 
            "result": "Request timed out"
        }
        
    except httpx.ConnectError:
        logger.error(f"Connection error to agent at {url} for PID {pid}")
        return {
            "pid": pid, 
            "status": 502, 
            "result": f"Cannot connect to agent at {url}"
        }
        
    except Exception as e:
        logger.exception(f"Unexpected error while killing PID {pid}")
        return {
            "pid": pid, 
            "status": 500, 
            "result": str(e)
        }

@router.post("/TaskManager/kill_process")
async def kill_process_endpoint(req: KillRequest):
    agent_ip = req.IP or req.host
    agent_port = 8100
    url = f"http://{agent_ip}:{agent_port}/kill"
    api_key = "myTopSecretKey321!" # Note: Still hardcoded as per instructions
    
    logger.info(f"Received request to kill PIDs {req.pids} on agent {agent_ip}")
    if not req.pids:
        raise HTTPException(status_code=400, detail="No PIDs provided")
    
    async with httpx.AsyncClient() as client:
        tasks = [kill_single_pid(client, url, pid, api_key) for pid in req.pids]
        results = await asyncio.gather(*tasks)
    
    # Determine the overall status code
    overall_status = 200
    for res in results:
        status = res.get("status", 200)
        if status >= 400:
            # Prioritize 504 over others, then 5xx, then 4xx
            if overall_status == 200 or status == 504 or (status >= 500 and overall_status < 500):
                overall_status = status

    logger.info(f"Completed kill process request for {len(req.pids)} PIDs with overall status {overall_status}")
    return JSONResponse(status_code=overall_status, content={"results": results})
