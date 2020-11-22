import file_handler

class Client:
    def __init__(self):
        print("hello world")

    #initialize client
    #do stuff here

    def createTorrentPayload(self, filename):
        """
        Creates the minimum torrent payload to POST to the tracker. The tracker will then create the actual torrent and assign it
        the unique ID, list of peers, and so on. The client will need to provide the filename and number of pieces.
        """
        pieces, numPieces = file_handler.encodeToBytes(filename)

        #create Peer2Server Message Buffer here.. defined in protocol.py
        
        #call send_msg to server

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

    