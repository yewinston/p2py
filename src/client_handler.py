"""
Handler class for taking in user's inputs.
"""

from src.client import *
from src.protocol import *
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
                    torrent_id = int(input("[p2py client] Please enter the torrent id: "))
                    return [OPT_GET_TORRENT, torrent_id, None]

                # Upload a file
                elif userInput == 3:
                    filename = str(input("[p2py client] Please enter the filename.ext: "))
                    return [OPT_UPLOAD_FILE, None, filename]
                
                elif userInput == 4:
                    print("\n///////////////////////////////////////////////////////////////////////////////////////////////////\n")
                    print("[1] Get & display list of torrents:")
                    print("\t - this option allows you to get a list of torrents and their associated torrent IDs (TID)\n")

                    print("[2] Download Torrent:")
                    print("\t - specify a torrent ID (TID) from the [1] list of torrents option to begin downloading a file\n")

                    print("[3] Upload a new file:")
                    print("\t - specify a file with format: [filename].[extension] , to add it to the torrent list.")
                    print("\t - you will begin seeding for this file")
                    print("\n///////////////////////////////////////////////////////////////////////////////////////////////////\n")
                    input("Press enter to continue...")
                    return [0, None, None]
                
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
    args = len(sys.argv) - 1

    if args == 4:
        src_ip = sys.argv[1]
        src_port = sys.argv[2]
        dest_ip = sys.argv[3]
        dest_port = sys.argv[4]
        
        try:
            asyncio.streams.socket.inet_aton(src_ip)
            asyncio.streams.socket.inet_aton(dest_ip)
        except asyncio.streams.socket.error:
            print("Incorrect format for source or tracker IP, please try again.")
            return None, None, None, None

        try:
            if int(src_port) not in range(0, 65536) or int(dest_port) not in range(0, 65536):
                print("Port range must be [0, 65535], please try again.")
                return None, None, None, None

        except ValueError:
            print("Incorrect format for source or tracker port given, please try again.")

    elif args == 2:
        src_ip = sys.argv[1]
        src_port = sys.argv[2]

        try:
            asyncio.streams.socket.inet_aton(src_ip)
        except asyncio.streams.socket.error:
            print("Incorrect format for source or tracker IP, please try again.")
            return None, None, None, None

        try:
            if int(src_port) not in range(0, 65536):
                print("Port range must be [0, 65535], please try again.")
                return None, None, None, None

        except ValueError:
            print("Incorrect format for source or tracker port given, please try again.")
        
    else:
        print("Please double check arguments:")
        print("client_handler.py [source ip] [source port] [tracker_ip] [tracker_port]")

    return src_ip, src_port, dest_ip, dest_port

async def main():
    src_ip, src_port, dest_ip, dest_port = parseCommandLine()
    
    if src_ip != None and src_port != None:
        cli = Client(src_ip, src_port)

        if dest_ip == None and dest_port == None:
            # Use default IP and port
            dest_ip = "127.0.0.1"
            dest_port = "8888"
        
        print("Connecting to tracker at " + dest_ip + ":" + dest_port + " ...")
        print("Connecting as client: " + src_ip + ":" + src_port + " ...")
        
        while True:
            reader, writer = await cli.connectToTracker(dest_ip, dest_port)

            argList = handleUserChoice()

            if argList[0] > 0:
                payload = cli.createServerRequest(opc=argList[0], torrent_id=argList[1], filename=argList[2])

                # NOTE: hacky way to handle invalid file handling (we pass an empty payload)
                if not payload:
                    continue

                # scenario 1: send a message
                await cli.send(writer, payload)

                # scenario 2: receive a message
                result = await cli.receive(reader)

                if result == RET_FINISHED_DOWNLOAD:
                    writer.close() # close original session, then start a new one
                    reader, writer = await cli.connectToTracker(dest_ip, dest_port)
                    payload = cli.createServerRequest(opc=OPT_START_SEED, torrent_id=argList[1])
                    await cli.send(writer, payload)
                    result = await cli.receive(reader)
                    writer.close()
                    
                #finished seeding, send server msg to remove status as seeder
                if result == RET_FINSH_SEEDING:   
                    writer.close() # close original session, then start a new one
                    reader, writer = await cli.connectToTracker(dest_ip, dest_port)
                    payload = cli.createServerRequest(opc = OPT_STOP_SEED, torrent_id=cli.tid)
                    await cli.send(writer, payload) #send msg to tracker
                    result = await cli.receive(reader)
                    writer.close()
                    break

                if result != RET_SUCCESS:
                    writer.close()

            # Help
            elif argList[0] == 0:
                writer.close()
            
            # Exit
            else:
                writer.close()
                sys.exit(0)

        writer.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting the program.")