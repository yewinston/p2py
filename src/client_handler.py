"""
Handler class for taking in user's inputs.
"""

from client import *
import protocol as p
import file_handler
import asyncio
import sys

async def connectToTracker(ip, port, cli):
    if ip == None and port == None:
        # Default IP and Port
        ip = "127.0.0.1"
        port = 8888
    
    try:
        print("Connecting to " + ip + ":" + str(port) + "...")
        reader, writer = await asyncio.open_connection(ip, int(port))
        
        opt = handleUserChoice()
        payload = cli.handleServerRequest(opc=opt, ip=ip, port=port)
        print("[PEER] Debug: sending payload:", payload)

        writer.write(payload.encode())
        data = await reader.read(100)

        print(f'[PEER] Received: {json.loads(data.decode())!r}')

        writer.close()

    except ConnectionError:
        print("Connection Error: unable to connect to tracker.")
        sys.exit(-1) # different exit number can be used, eg) errno library

def handleUserChoice():
    while True:
        print("\nWelcome to p2py.")
        print("[1] Get list of torrents")
        print("[2] Upload a new file")
        print("[3] Exit")
        userInput = int(input("[p2py client]: Choose an option: "))
        
        # TODO: error checking for input
        if userInput in range(0,3):
            if userInput == 1:
                print("\n[PEER] Get list")
                return p.OPT_GET_LIST

            elif userInput == 2:
                print("\n[TODO] Upload new file")
                return p.OPT_UPLOAD_FILE

            elif userInput == 3:
                sys.exit(0)
    
        else:
            print("Invalid input. Please try again.")

def parseCommandLine():
    ip = None
    port = None

    if len(sys.argv) > 0:
        if "-i" in sys.argv and "-p" in sys.argv:
            # TODO: error checking
            ip = sys.argv[sys.argv.index("-i") + 1]
            port = sys.argv[sys.argv.index("-p" + 1)]
    return ip, port

def main():
    cli = Client()
    ip, port = parseCommandLine()
    asyncio.run(connectToTracker(ip, port, cli))
    
    # scenario 1: send a message
    # message = cli.createTorrentPayload("../files/sample.txt")
    # cli.send("socket", message)

    # # scenario 2: receive a message
    # cli.handleServerResponse(message)
    
if __name__ == "__main__":
    main()