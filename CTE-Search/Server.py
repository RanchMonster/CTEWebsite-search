from asyncio import sleep, create_task, get_event_loop
import websockets as ws
from Cache import CacheHandle
from LogManager import *

import time
def temp_testing():
    time.sleep(3)

async def handle_server(websocket: ws.ServerConnection):
    try:
        await websocket.send("hello world")
        while True:
            message = await websocket.recv()
            info(f"from: websocket:{websocket.remote_address}  recv:{str(message)}")
            response = f"Server received: {message}"
            await asyncio.to_thread(temp_testing) # sim waiting for the model could take longer I am hoping since most of scikit and stuff is in c it will stop the gil from casuing it to be too slow
            await websocket.send(response)
    except ws.ConnectionClosed as e:
        error(f"disconnected: {str(e)} ")
async def handle_model(query):
    cache = CacheHandle.load()
    model = None
    if "model" in cache:
        model = cache.model
    else: 
        critical("No trained model stored please retrain")

async def start_server():
    cache = CacheHandle.load()
    # set the values in this context so we can change the refernce to it later
    adrrs = "0.0.0.0" # Set the default value so there is no error
    port = None # This can be none by default
    if "settings" in cache:
        for x in cache.settings:
            if x.name == "address":
                adrrs = x.value
            elif x.name == "port":
                port = x.value
    server = await ws.serve(
        handler=handle_server,
        host=adrrs,
        port=int(port)
    )
    info(f"WebSocket server started on ws://{adrrs}:{port or "80"}")
    await server.wait_closed()
    info("Server closed")

