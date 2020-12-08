"""
Provides Client's functionalities and actions. See client_handler which is the main entry point for user interaction handling
"""
from src.protocol import *
import src.file_handler as fd
from socket import *
import json
import asyncio
import sys
import uuid
import hashlib
import threading
class Client:
    def __init__(self, src_ip, src_port):
        self.src_ip = src_ip
        self.src_port = src_port
        self.peer_id = self.createPeerID()
        self.tid = -1
        # Peer States
        self.peer_choked = True
        self.peer_interested = False
        self.peer_am_seeding = False
        self.peer_am_leeching = False

        # List of seeders & piece buffer associated to the current download 
        self.seeders_list = dict()
        self.piece_buffer = PieceBuffer()


########### CONNECTION HANDLING ###########

    async def connectToTracker(self, ip, port):
        """
        Handles connecting to the tracker and returns the reader and writer.
        """
        if ip == None and port == None:
            # Use default IP and port
            ip = "127.0.0.1"
            port = "8888"
    
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            return reader, writer

        except ConnectionError:
            print("Connection Error: unable to connect to tracker.")
            sys.exit(-1) # different exit number can be used, eg) errno library

    async def connectToPeer(self, ip, port, requests):
        """
        This function handles both sending the payload request, and receiving the expected response
        """
        # NOTE: This has same issue as above note in connectToTracker, although I don't think we can take the "printing" out of this one. We can leave these prints.
        try:
            print("Connecting to seeder at " + ip + ":" + port + " ...")
            reader, writer = await asyncio.open_connection(ip, int(port))
            print("Connected as leecher: " + self.src_ip + ":" + self.src_port + ".")

        except ConnectionError:
            print("Connection Error: unable to connect to peer.")
            sys.exit(-1) # different exit number can be used, eg) errno library

        await self.send(writer, requests)
        res = await self.receive(reader)
        writer.close()

    async def receiveRequest(self, reader, writer):
        """
        Handle incoming PEER requests and returns the appropriate response object
        """
        try:
            data = await reader.read(READ_SIZE)

            peerRequest = json.loads(data.decode())
            addr = writer.get_extra_info('peername')

            print(f"\n[PEER] Debug received {peerRequest!r} from {addr!r}.")
            response = self.handlePeerRequest(peerRequest)
            payload = json.dumps(response)
            print("[PEER] Debug send payload:", payload)
            writer.write(payload.encode())
            await writer.drain()
            print("[PEER] Closing the connection for", addr)
        except:
            print("[PEER] Peer", writer.get_extra_info('peername'), "has disconnected.")
        
        writer.close() 

    async def startSeeding(self):
        """
        Once a client begins seeding, we need to open and host a connection as a 'server'
        """
        server = await asyncio.start_server(self.receiveRequest, self.src_ip, self.src_port)
        if (server is None):
            return
        addr = server.sockets[0].getsockname()
        print(f'[PEER] SEEDING !!! ... Serving on {addr}\n')
        loop = asyncio.get_event_loop()
        async with server:
            try: 
                await server.serve_forever()
            except:
                pass
            finally:
                server.close()
                await server.wait_closed()

    async def receive(self, reader):
        """
        Handle incoming RESPONSE messages and decode to the JSON object.
        Pass the JSON object to handleRequest() that will handle the request appropriately.
        """
        data = await reader.read(READ_SIZE)
        payload = json.loads(data.decode())
        print(f'[PEER] Received decoded message: {payload!r}\n')
        opc = payload[OPC]
        if opc > 9:
            res = await self.handleServerResponse(payload)
        else:
            res = self.handlePeerResponse(payload)
        
        return res
    

    async def send(self, writer, payload:dict):
        """
        Encode the payload to an encoded JSON object and send to the appropriate client/server
        """
        jsonPayload = json.dumps(payload)
        print("[PEER] Sending encoded request message:", (jsonPayload))
        writer.write(jsonPayload.encode())
    

########### REQUEST & RESPONSE HANDLING ###########

    async def handleServerResponse(self, response) -> int:
        """
        Handle the response from a server, presumably a python dict has been loaded from the JSON object.
        Returns the appropriate RET code to client_handler.
        """
        ret = response[RET]
        opc = response[OPC]

        # RET Handling
        if ret == RET_FAIL:
            print("[PEER] RESPONSE: returned failed")
            return -1
        elif ret == RET_ALREADY_SEEDING:
            print("[PEER] UPLOAD FAIL: You are already currently seeding a file.")
            return -1
        elif ret == RET_NO_AVAILABLE_TORRENTS:
            print("[PEER] GET TORRENT LIST FAIL: There are no available torrents right now.")
            return -1
        elif ret == RET_TORRENT_DOES_NOT_EXIST:
            print("[PEER] GET TORRENT FAIL: The torrent ID does not exist")
            return -1

        # If RET_SUCCESS, handle the response payload based on OPC
        if opc == OPT_GET_LIST:
            torrent_list = response[TORRENT_LIST]
            print("\n///////////////////////////////////////////////////////////////////////////////////////////////////\n")
            print("TID \t FILE_NAME \t TOTAL_PIECES \t SEEDERS \t")
            print("--- \t -------- \t ------------ \t ------- \t")
            for idx, curr_torrent in enumerate(torrent_list):
                print(curr_torrent[TID], '\t', curr_torrent[FILE_NAME], '\t',  curr_torrent[TOTAL_PIECES], '\t\t', curr_torrent[SEEDER_LIST], '\n')
            print("\n///////////////////////////////////////////////////////////////////////////////////////////////////\n")
            return RET_SUCCESS
        elif opc == OPT_GET_TORRENT:
            torrent = response[TORRENT]
            self.peer_am_leeching = True
            self.seeders_list = torrent[SEEDER_LIST]
            self.piece_buffer.setBuffer(torrent[TOTAL_PIECES])
            #we immediately start the downloading process upon receiving the torrent object
            await self.downloadFile(torrent[TOTAL_PIECES], torrent[FILE_NAME])
            return RET_FINISHED_DOWNLOAD    
        elif opc == OPT_START_SEED or opc == OPT_UPLOAD_FILE:
            self.peer_am_leeching = False
            self.peer_am_seeding = True
            self.tid = response[TID]
            await self.startSeeding()
            return RET_FINSH_SEEDING
        elif opc == OPT_STOP_SEED:
            self.peer_am_seeding = False
            return RET_FINSH_SEEDING

        return 1

    def createServerRequest(self, opc:int, torrent_id=None, filename=None) -> dict:
        """
        Called from client_handler.py to create the appropriate server request given the op code
        Returns a dictionary of our payload.
        """
        payload = {OPC:opc, IP:self.src_ip, PORT:self.src_port, PID:self.peer_id}
        # get list of torrents is default payload as above

        if opc == OPT_GET_TORRENT or opc == OPT_START_SEED or opc == OPT_STOP_SEED:
            payload[TID] = torrent_id
        elif opc == OPT_UPLOAD_FILE:
            numPieces = self.uploadFile(filename)
            
            # NOTE: hacky way to handle the invalid file exception
            if numPieces == 0:
                return {}

            payload[FILE_NAME] = self.fileStrip(filename)
            payload[TOTAL_PIECES] = numPieces

        return payload

    def handlePeerResponse(self, response) -> int:
        """
        Handle the response from a peer. Returns 1 if successful 
        """
        ret = response[RET]
        opc = response[OPC]

        if ret == RET_FAIL or ret != RET_SUCCESS:
            return -1
        
        if opc == OPT_GET_PEERS:
            self.seeders_list = response[PEER_LIST]
        elif opc == OPT_GET_PIECE:
            data = response[PIECE_DATA]
            idx = response[PIECE_IDX]
            newPiece = Piece(idx, data)
            self.piece_buffer.addData(newPiece)
        
        return 1

    def handlePeerRequest(self, request) -> dict():
        """
        Handle the incoming request (this applies to peers only). Returns a response dictionary object.
        """
        opc = request[OPC]
        response = {OPC: opc, IP:self.src_ip, PORT:self.src_port}

        if opc == OPT_GET_PEERS:
            response[PEER_LIST] = self.seeders_list
            response[RET] = RET_SUCCESS
        elif opc == OPT_GET_PIECE:
            piece_idx = request[PIECE_IDX]
            if self.piece_buffer.checkIfHavePiece(piece_idx):
                response[PIECE_DATA] = self.piece_buffer.getData(piece_idx)
                response[PIECE_IDX] = request[PIECE_IDX]
                response[RET] = RET_SUCCESS
            else:
                response[RET] = RET_FAIL
        return response
        
    def createPeerRequest(self, opc:int, piece_idx=None) -> dict:
        """
        Create the appropriate peer request.
        """
        payload = {OPC:opc, IP:self.src_ip, PORT:self.src_port}

        if opc == OPT_GET_PIECE:
            payload[PIECE_IDX] = piece_idx
        
        return payload


########### HELPER FUNCTIONS ###########

    # NOT USED
    async def simplePeerSelection(self, numPieces:int):
        """
        A simple peer selection that downloads and entire file from the first peer in list
        """
        # assuming here peer_list is a dictionary. Just grab the first one to be the seeder.
        # this code requires py 3.6+
        pid = next(iter(self.seeders_list))
        initialPeer_ip = self.seeders_list[pid][IP]
        initialPeer_port = self.seeders_list[pid][PORT]
        
        for idx in range(numPieces):
            request = self.createPeerRequest(OPT_GET_PIECE, idx)
            await self.connectToPeer(initialPeer_ip, initialPeer_port, request)
        
    async def evenPeerSelection(self, numPieces:int):
        """
        Evenly distributes the piece requests among available peers
        """
        numPeers = len(self.seeders_list)

        peerList = []             # Add peers to a list
        requests_list = []        # Add requests to a list

        for peer in self.seeders_list.values():
            peerList.append(peer)
        for i in range(numPieces):
            requests_list.append(self.createPeerRequest(OPT_GET_PIECE, i))
        
        currPiece = 0
        while (currPiece < numPieces):
            currPeer = currPiece % numPeers
            await self.connectToPeer(peerList[currPeer][IP], peerList[currPeer][PORT], requests_list[currPiece])
            currPiece +=1   
        
    async def downloadFile(self, numPieces:int, filename:str):
        """
        Method for starting the download of a file by calling the peer selection method to download pieces
        Once done, output it to the output directory with peer_id appended to the filename.
        """
        await self.evenPeerSelection(numPieces)

        while not self.piece_buffer.checkIfHaveAllPieces:
            continue
        
        pieces2file = []
        outputDir = 'output/' + self.peer_id + '_' + filename
        for i in range(self.piece_buffer.getSize()):
            pieces2file.append(self.piece_buffer.getData(i))

        try:
            fd.decodeToFile(pieces2file, outputDir)
            print("[PEER] Successfully downloaded file: ", outputDir)
        except:
            print("Exception occured in downloadFile() with filename:", filename)
        

    def uploadFile(self, filename: str) -> int:
        """
        Called when the user begins to be the initial seeder (upload a file). The piecebuffer will be
        populated and initialized.
        Returns the number of pieces in the created piece buffer.
        """
        pieces = []
        numPieces = 0
        try:
            pieces, numPieces = fd.encodeToBytes(filename)
        except:
            print("Exception occured in uploadFile() with filename:", '\''+filename+'\'', ", please check your filename or directory.")
            return 0
           
        # Set the buffer size and add the file's data to the buffer.
        self.piece_buffer.setBuffer(numPieces)

        for idx in range(len(pieces)):
            currPiece = Piece(idx, pieces[idx])
            self.piece_buffer.addData(currPiece)      

        return numPieces

    def createPeerID(self) -> str:
        """
        Ideally, create a unique peer ID.
        Uses src_ip + src_port and MD5 hash -> hexadecimal string as an ID.
        """
        hashString = self.src_ip+self.src_port
        return hashlib.md5(hashString.encode()).hexdigest()

    def fileStrip(self, filename) -> str:
        """
        Strips the filename from directory path and escape characters
        """
        size = len(filename)
        stripped = ""
        for idx in range(size-1, -1, -1):
            if filename[idx] == "/" or filename[idx] == "\'":
                break
            else:
                stripped+=filename[idx]

        # this reverses the string
        return stripped[::-1]
        
class Piece:
    """
    Files are split into pieces 
    index -> piece's index in the expected buffer

    """
    def __init__(self, index: int, data):
        self.index = index
        self.data = data

class PieceBuffer:
    """
    A piece manager that handles the current piece buffer for the requested file
    """

    def __init__(self):
        self.__buffer = []
        self.__size = 0
        self.__havePieces = []
    
    def getBuffer(self):
        return self.__buffer

    def setBuffer(self, length: int):
        """
        Initialize the piece buffer given the total number of pieces for the expected file
        """
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

    def getData(self, idx: int):
        """
        Returns the piece bytes at the specified index.
        """
        if idx < 0 or idx >= self.__size or self.__buffer[idx] == 0:
            return -1
        else:
            return self.__buffer[idx]
            
    def getSize(self) -> int:
        return self.__size

    def getMissingPieces(self) -> [int]:
        missingPieces = []
        for idx, pce in enumerate(self.__havePieces):
            if not pce:
                missingPieces.append(idx)
        return missingPieces
    
    def checkIfHavePiece(self, idx:int) -> bool:
        return self.__havePieces[idx]
    
    def checkIfHaveAllPieces(self) -> bool:
        for pce in self.__havePieces:
            if not pce:
                return False
        return True
    


    