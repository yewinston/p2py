"""
Handler class for taking in user's inputs.
"""

from client import *
import file_handler

def parseCommandLine():
    print("parse command line todo")

def main():
    cli = Client()
    
    # scenario 1: send a message
    message = cli.createTorrentPayload("../files/sample.txt")
    cli.send("socket", message)

    # scenario 2: receive a message
    cli.handleServerResponse(message)

    
if __name__ == "__main__":
    main()