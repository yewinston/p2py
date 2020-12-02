"""
Provides Client's functionalities and actions. See client_handler which is the main entry point for user interaction handling
"""
import protocol
import file_handler
import json
from socket import *

class Client:
    def __init__(self):
        return

    def handleServerRequest(self, opc, ip, port, peer_id=None, torrent_id=None, filename=None, numPieces=None):
        """
        Builds the Request message. Returns as a json object that is encoded into bytes.
        """
        payload = {"opc": opc, "ip": ip, "port": port, "peer_id": peer_id, "torrent_id": torrent_id, "filename": filename, "numPieces": numPieces}
        return json.dumps(payload)

    def handleServerResponse(self, response):
        """
        Handle the Response message.
        """
        json.loads(response)
        print("handling response:", response)


    def send(self, socket, request):
        """
        Defined our own send function in case we need to do any modifications.
        """

        # socket.send(request)
        
        print("sending encoded request message:", request.encode())


    def receive(self, socket, port):
        try:
            response = socket.recvfrom(port)[0].decode()
        except:
            print("Client::receive() error")
            response = None
    
        handleServerResponse(response)

    def createTorrentPayload(self, filename):
        """
        Creates the minimum torrent payload to POST to the tracker. The tracker will then create the actual torrent and assign it
        the unique ID, list of peers, and so on. The client will need to provide the filename and number of pieces.
        """

        # when we "upload" a file to the server, we need to create a 'pieces' state so that clients can now request for it.
        pieces, numPieces = file_handler.encodeToBytes(filename)
        return self.handleServerRequest(protocol.OPT_UPLOAD_FILE, "127.0.0.1", "8080", 123, None, filename, numPieces)


class PieceBuffer:
    """
    A piece manager that handles the current piece buffer for the requested file
    """

    def __init__(self, torrent):
        #the torrent should contain metadata about the download.. not sure what the format of the torrent will be at this moment
        self.torrent = torrent

        #something like...
        self.size = torrent.numPieces

        # a boolean list to determine which pieces have been received.
        self.havePieces = [False for i in range(torrent.numPieces)]
        self.buffer = []

class Piece:
    """
    Files are split into pieces 
    index -> piece's index in the expected buffer

    """
    def __init__(self, index: int, data: bytes, length: int):
        self.index = index
        self.data = data
        self.length = length

    