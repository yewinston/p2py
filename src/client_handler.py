"""
Handler class for taking in user's inputs.
"""

from client import *
from protocol import *
import file_handler
import asyncio
import sys

def handleUserChoice():
    while True:
        print("\nChoose an option: ")
        print("[1] Get & display list of torrents")
        print("[2] Download Torrent")
        print("[3] Upload a new file")
        print("[4] Help")
        print("[5] Exit")
        userInput = input("[p2py client]: ")
        
        try:
            userInput = int(userInput)
            
            if userInput in range(0,6):
                # Get list of torrents
                if userInput == 1:
                    print("\n[PEER] Get list of torrents")
                    return [OPT_GET_LIST, None, None]

                # Get a torrent
                elif userInput == 2:
                    # NOTE we need error check.. like if the torrent id doesnt exist?
                    torrent_id = int(input("[p2py client] Please enter the torrent id: "))
                    return [OPT_GET_TORRENT, torrent_id, None]

                # Upload a file
                elif userInput == 3:
                    filename = str(input("[p2py client] Please enter the filename.ext: "))
                    return [OPT_UPLOAD_FILE, None, filename]
                
                elif userInput == 4:
                    print("TODO: Heres some helpful stuff.")
                    return -1
                
                # Quitting
                elif userInput == 5:
                    return [-1, None, None]
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
        
        while True:
            reader, writer = await cli.connectToTracker(dest_ip, dest_port)

            # NOTE - need a better way of getting user inputs. Currently just have "None" if the field is not used
            argList = handleUserChoice()

            if argList[0] > 0:
                payload = cli.createServerRequest(opc=argList[0], torrent_id=argList[1], filename=argList[2])

                # NOTE: hacky way to handle invalid file handling (we pass an empty payload)
                if not payload:
                    writer.close()
                    return

                # scenario 1: send a message
                await cli.send(writer, payload)

                # scenario 2: receive a message
                result = await cli.receive(reader)

                if result == RET_FINISHED_DOWNLOAD:
                    reader, writer = await cli.connectToTracker(dest_ip, dest_port)
                    payload = cli.createServerRequest(opc=OPT_START_SEED, torrent_id=0)
                    await cli.send(writer, payload)
                    result = await cli.receive(reader)

                    
                elif result != RET_SUCCESS:
                    writer.close()
            else:
                writer.close()
                sys.exit(0)

        writer.close()
if __name__ == "__main__":
    asyncio.run(main())