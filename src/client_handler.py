"""
Handler class for taking in user's inputs.
"""

from client import *
import protocol as p
import file_handler
import asyncio
import sys

def handleUserChoice():
    while True:
        print("\nChoose an option: ")
        print("[1] Get list of torrents")
        print("[2] Upload a new file")
        print("[3] Exit")
        userInput = input("[p2py client]: ")
        
        try:
            userInput = int(userInput)
            
            if userInput in range(0,4):
                if userInput == 1:
                    print("\n[PEER] Get list of torrents")
                    return p.OPT_GET_LIST

                elif userInput == 2:
                    print("\n[TODO] Upload new file")
                    return p.OPT_UPLOAD_FILE

                elif userInput == 3:
                    return -1
            else:
                print("Invalid input. Please try again.")
        except ValueError:
            print("Invalid input, only integer values allowed.")

def parseCommandLine():
    ip = None
    port = None

    if len(sys.argv) > 0:
        if "-i" in sys.argv and "-p" in sys.argv:
            # TODO: error checking
            ip = sys.argv[sys.argv.index("-i") + 1]
            port = sys.argv[sys.argv.index("-p") + 1]
    return ip, port

async def main():
    cli = Client()
    ip, port = parseCommandLine()

    reader, writer = await cli.connectToTracker(ip, port)
    opt = handleUserChoice()

    if opt > 0:
        payload = cli.createServerRequest(opc=opt, ip=ip, port=port)
        # print("[PEER] Debug payload:", payload)

        # scenario 1: send a message
        await cli.send(writer, payload)

        # scenario 2: receive a message
        await cli.receive(reader)
    writer.close()
    
if __name__ == "__main__":
    asyncio.run(main())