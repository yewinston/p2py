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
    src_ip = None
    src_port = None
    dest_ip = None
    dest_port = None

    if len(sys.argv) - 1 == 4:
        # TODO: error checking
        src_ip = sys.argv[1]
        src_port = sys.argv[2]
        dest_ip = sys.argv[3]
        dest_port = sys.argv[4]
    elif len(sys.argv) - 1 == 2:
        src_ip = sys.argv[1]
        src_port = sys.argv[2]
    else:
        print("Please double check arguments:")
        print("client_handler.py [source ip] [source port] [tracker_ip] [tracker_port]")
    return src_ip, src_port, dest_ip, dest_port

async def main():
    src_ip, src_port, dest_ip, dest_port = parseCommandLine()
    
    if src_ip != None and src_port != None:
        cli = Client(src_ip, src_port)

        reader, writer = await cli.connectToTracker(dest_ip, dest_port)
        opt = handleUserChoice()

        if opt > 0:
            payload = cli.createServerRequest(opc=opt)
            # print("[PEER] Debug payload:", payload)

            # scenario 1: send a message
            await cli.send(writer, payload)

            # scenario 2: receive a message
            await cli.receive(reader)
        writer.close()
    
if __name__ == "__main__":
    asyncio.run(main())