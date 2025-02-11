from asyncio import sleep, create_task, get_event_loop
import websockets as ws
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
    server = await ws.serve(
        handler=handle_server,
        host="0.0.0.0",
        port=8765  # Specify your desired port
    )
    info("WebSocket server started on ws://0.0.0.0:8765")
    await server.wait_closed()
    info("Server closed")

