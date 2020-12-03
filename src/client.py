"""
Provides Client's functionalities and actions. See client_handler which is the main entry point for user interaction handling
"""
from protocol import *
import file_handler
import json
import asyncio
from socket import *

class Client:
    def __init__(self):
        self.peer_id = self.createPeerID()
        self.piece_buffer = PieceBuffer()
        self.peer_choked = True
        self.peer_interested = False
        self.peer_am_seeding = False
        self.peer_am_leeching = False

########### CONNECTION HANDLING ###########

    async def receive(self, reader, writer):
        """
        Handle incoming requests and decode to the JSON object.
        Pass the JSON object to handleRequest() that will handle the request appropriately.
        """
        print("todo") 

    def send(self, payload:dict):
        """
        Encode the payload to an encoded JSON object and send to the appropriate client/server
        ? Do we automatically know who to send it to ?
        """
        # socket.send(request)
        print("sending encoded request message:", (json.dumps(payload)).encode())


########### REQUEST & RESPONSE HANDLING ###########

    def handleServerResponse(self, response) -> int:
        """
        Handle the response from a server, presumably a python dict has been loaded from the JSON object.
        Note: The delegation must be handled elsewhere (i.e. in receive()) to determine whether its SERVER or PEER response using OPC 
        """
        ret = response[RET]
        opc = response[OPC]

        if ret == RET_FAIL or ret != RET_SUCCESS:
            return -1
        
        if opc == OPT_GET_LIST:
            torrent_list = response[TORRENT_LIST]
            print("todo: print the results?")
        elif opc == OPT_GET_TORRENT:
            torrent = response[TORRENT]
            self.piece_buffer.setBuffer(torrent.TOTAL_PIECES)
            print("todo: start the downloading process..")
        elif opc == OPT_START_SEED or opc == OPT_UPLOAD_FILE:
            self.peer_am_seeding = True
            print("todo: allow seeding... the user should not be able to download other files?")
        elif opc == OPT_STOP_SEED:
            self.peer_am_seeding = False
            print("todo: allow the user to regain control?")

        return 1

    def createServerRequest(self, opc:int, ip:str, port:str, torrent_id=None, filename=None) -> dict:
        """
        Called from client_handler.py to create the appropriate server request given the op code
        Returns a dictionary of our payload.
        """
        payload = {OPC:opc, IP:ip, PORT:port, PID:self.peer_id}
        # get list of torrents is default payload as above

        if opc == OPT_GET_TORRENT or opc == OPT_START_SEED or opc == OPT_STOP_SEED:
            payload[TID] = torrent_id
        elif opc == OPT_UPLOAD_FILE:
            numPieces = self.uploadFile(filename)
            payload[FILE_NAME] = filename
            payload[TOTAL_PIECES] = numPieces

        return payload

    def handlePeerResponse(self, response):
        """
        Handle the response from a peer.
        """
        ret = response[RET]
        opc = response[OPC]

        if ret == RET_FAIL or ret != RET_SUCCESS:
            return -1
        
        if opc == OPT_GET_PEERS:
            peers_list = response[PEER_LIST]
            print("do something with peer list..")
        elif opc == OPT_GET_PIECE:
            data = response[PIECE_DATA]
            idx = response[PIECE_IDX]
            newPiece = Piece(idx, data)
            self.piece_buffer.addData(newPiece)
            print('do more..')

    def handlePeerRequest(self, request):
        """
        Handle the incoming request (this applies to peers only)
        """
        
        if opc == OPT_STATUS_INTERESTED:
            print('todo')
        elif opc == OPT_STATUS_UNINTERESTED:
            print('todo')
        elif opc == OPT_STATUS_CHOKED:
            print('todo')
        elif opc == OPT_STATUS_UNCHOKED:
            print('todo')
        elif opc == OPT_GET_PEERS:
            print('todo')
        elif opc == OPT_GET_PIECE:
            print('todo')
        
        
    def createPeerRequest(self, opc:int, ip:str, port:str, piece_idx=None) -> dict:
        """
        Create the appropriate peer request.
        """
        payload = {OPC:opc, IP:ip, PORT:port}

        if opc == OPT_GET_PIECE:
            payload[PIECE_IDX] = piece_idx
        
        return payload


########### HELPER FUNCTIONS ###########

    def uploadFile(self, filename: str) -> int:
        """
        Called when the user begins to be the initial seeder (upload a file). The piecebuffer will be
        populated and initialized.
        Returns the number of pieces in the created piece buffer.
        """
        try:
            pieces, numPieces = file_handler.encodeToBytes(filename)
        except:
            print("Exception occured in uploadFile() with filename:", filename)

        # Set the buffer size and add the file's data to the buffer.
        self.piece_buffer.setBuffer(numPieces)
        for idx in range(len(pieces)):
            currPiece = Piece(idx, pieces[idx])
            self.piece_buffer.addData(currPiece)

        return numPieces

    def createPeerID(self) -> int:
        """
        Ideally, create a unique peer ID... maybe need a hashing function
        """
        return 1

class PieceBuffer:
    """
    A piece manager that handles the current piece buffer for the requested file
    """

    def __init__(self):
        self.__buffer = []
        self.__size = 0
        self.__havePieces = []
    
    def getBuffer(self) -> [bytes]:
        return self.__buffer

    def setBuffer(self, length: int):
        self.__buffer = [0] * length
        self.__size = length
        self.__havePieces = [False] * length

    def addData(self, piece: Piece) -> int:
        idx = piece.index
        data = piece.data
        if idx < 0 or idx >= self.__size:
            return -1
        else:
            self.__buffer[idx] = data
            self.__havePieces[idx] = True
            return 1

    def getData(self, idx: int) -> Piece:
        if idx < 0 or idx >= self.__size or self.__buffer[idx] == 0:
            return -1
        else:
            piece = Piece(idx, self.__buffer[idx])
            return piece

    def getSize(self) -> int:
        return self.__size

    def getMissingPieces(self) -> [int]:
        missingPieces = []
        for idx, pce in enumerate(self.__havePieces):
            if not pce:
                missingPieces.append(idx)
        return missingPieces
    
class Piece:
    """
    Files are split into pieces 
    index -> piece's index in the expected buffer

    """
    def __init__(self, index: int, data: bytes):
        self.index = index
        self.data = data
        self.length = length

    