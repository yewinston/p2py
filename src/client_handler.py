"""
Handler class for taking in user's inputs.
"""

from client import *
import file_handler
import sys

def parseCommandLine():
    for arg in sys.argv:
        print(arg)

def main():
    cli = Client()
    parseCommandLine()
    
    # scenario 1: send a message
    message = cli.createTorrentPayload("../files/sample.txt")
    cli.send("socket", message)

    # # scenario 2: receive a message
    cli.handleServerResponse(message)

    
if __name__ == "__main__":
    main()