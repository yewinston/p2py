import asyncio
import json

async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    print(f'Send: {message!r}')
    writer.write(message.encode())

    data = await reader.read(100)
    print(f'Received: {json.loads(data.decode())!r}')

    print('Close the connection')
    writer.close()

jsonObj = json.dumps({"test": 123, "test2": "string"})

asyncio.run(tcp_echo_client(jsonObj))