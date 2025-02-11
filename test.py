import asyncio
import websockets as ws

async def test_connection():
    uri = "ws://localhost:8765"
    async with ws.connect(uri) as websocket:
        # Receive initial hello world message
        initial_message = await websocket.recv()
        print(f"Received: {initial_message}")
        
        # Send test messages
        test_messages = ["Hello", "How are you?", "Testing 123"]
        for message in test_messages:
            await websocket.send(message)
            response = await websocket.recv()
            print(f"Sent: {message}")
            print(f"Received: {response}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(test_connection())
