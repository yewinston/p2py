import asyncio
import json

async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = json.loads(data.decode())

    addr = writer.get_extra_info('peername')

    print(f"Received {message!r} from {addr!r}")

    print("Appending to JSON object")
    message.update({"test3": "from the server"})

    print(f"Send: {message!r}")

    jsonObj = json.dumps(message)
    writer.write(jsonObj.encode())
    await writer.drain()

    print("Closing the connection")
    writer.close()

async def main():
    server = await asyncio.start_server(handle_echo, '127.0.0.1', 8888)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

asyncio.run(main())