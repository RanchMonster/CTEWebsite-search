from asyncio import sleep, create_task, get_event_loop, to_thread
import websockets as ws
from Cache import CacheHandle
from LogManager import *
from DataTypes import SearchQuery
from multiprocessing.pool import Pool
from typing import Callable
import json

# Global process pool for handling CPU-intensive tasks
__POOL = Pool()

async def quick_fork(target: Callable, *args, **kwargs):
    """
    Executes a CPU-intensive function in a separate process pool.
    
    Args:
        target (Callable): The function to execute
        *args: Positional arguments for the target function
        **kwargs: Keyword arguments for the target function
        
    Returns:
        The result of the target function
    """
    task =__POOL.apply_async(target, args, kwargs)
    if not task.ready():
        await sleep(0)
    else:
        return task.get()

async def handle_search(websocket: ws.ServerConnection):
    """
    Handles incoming search requests from websocket clients.
    
    Args:
        websocket (ws.ServerConnection): The websocket connection to the client
    """
    model = get_model()
    if model:
        query: SearchQuery = json.loads(await websocket.recv())
        results = await quick_fork(model.improved_search, query["query"], query["filters"])
        await websocket.send(json.dumps(results))
    else:
        critical("Failed to load model")

async def handle_server(websocket: ws.ServerConnection):
    """
    Main websocket connection handler that routes requests based on path.
    
    Args:
        websocket (ws.ServerConnection): The websocket connection to handle
    """
    try:
        if websocket.request.path == "/search":
            await handle_search(websocket)
    except ws.ConnectionClosed as e:
        error(f"disconnected: {str(e)}")

def get_model():
    """
    Retrieves the trained model from cache.
    
    Returns:
        The trained model if available, None otherwise
    """
    cache = CacheHandle.load()
    if "model" in cache:
        return cache.model
    else:
        critical("No trained model stored please retrain")
        return None

async def start_server():
    """
    Initializes and starts the websocket server using configuration from cache.
    Handles server lifecycle and logging.
    """
    cache = CacheHandle.load()
    # Default server configuration
    addr = "0.0.0.0"
    port = 80  # Set default port to standard websocket port
    if "settings" in cache:
        for setting in cache.settings:
            if setting.name == "address":
                addr = setting.value if setting.value != "" else addr
            elif setting.name == "port":
                port = setting.value if setting.value != 0 else port

    server = await ws.serve(
        handler=handle_server,
        host=addr,
        port=int(port)
    )
    
    info(f"WebSocket server started on ws://{addr}:{port}")
    await server.wait_closed()
    info("Server closed")
