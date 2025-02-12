from asyncio import sleep, create_task, get_event_loop
import websockets as ws
from Cache import CacheHandle
from LogManager import *
async def handle_server(websocket: ws.ServerConnection):
    try:
        await websocket.send("hello world")
        while True:
            message = await websocket.recv()
            info(f"from: websocket:{websocket.remote_address}  recv:{str(message)}")
            # Handle incoming messages here
            await asyncio.sleep(5) #sim waiting on the model 
            response = f"Server received: {message}"
            await websocket.send(response)
    except ws.ConnectionClosed as e:
        error(f"disconnected: {str(e)} ")

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
                port == port
    server = await ws.serve(
        handler=handle_server,
        host=adrrs,
        port=port
    )
    info(f"WebSocket server started on ws://{adrrs}:{port or "80"}")
    await server.wait_closed()
    info("Server closed")

