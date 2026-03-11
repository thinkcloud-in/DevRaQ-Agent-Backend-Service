from fastapi import APIRouter
import logging
import httpx

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/test")
async def test_backend():
    """Simple endpoint to verify the agent backend is running and reachable."""
    return {
        "status": "success",
        "message": "Agent backend is running and healthy"
    }

@router.get("/ping_agent")
async def ping_agent(host: str):
    """Test connectivity to an external agent on port 8100."""
    agent_port = 8100
    url = f"http://{host}:{agent_port}/" # Trying root or common health endpoints
    
    async with httpx.AsyncClient() as client:
        try:
            # We just want to see if the port is open and responding
            response = await client.get(url, timeout=5.0)
            return {
                "host": host,
                "port": agent_port,
                "reachable": True,
                "status_code": response.status_code,
                "message": "Agent is reachable"
            }
        except httpx.ConnectError:
            return {
                "host": host,
                "port": agent_port,
                "reachable": False,
                "message": f"Could not connect to agent at {host}:{agent_port}"
            }
        except httpx.TimeoutException:
            return {
                "host": host,
                "port": agent_port,
                "reachable": False,
                "message": f"Connection to agent at {host}:{agent_port} timed out"
            }
        except Exception as e:
            return {
                "host": host,
                "port": agent_port,
                "reachable": False,
                "message": f"Error: {str(e)}"
            }
