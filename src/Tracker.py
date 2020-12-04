from bencode import *
from torrent import *
# FIXME: would p be confusing for peer?
import protocol as p
import asyncio
import json

class TrackerServer:                              
    #torrent metadata
    def __init__(self):
        self.nextTorrentId = 1 
        self.torrent = {}              #the torrent list (dictionary), defined by its unique torrentID
        self.peers = {}                #distingueshed by peerId, value will be a dictionary that holds that user's information 

    def receiveRequest(self, req):          #the things that will be returned will be in dict form
        opc = req.get('opc')

        if opc == p.OPT_GET_LIST:
            return self.getTorrentDict()
        elif opc == p.OPT_GET_TORRENT:
            return self.getTorrentObject(req)
        elif opc == p.OPT_START_SEED:
            return self.updatePeerStatus(req)
        elif opc == p.OPT_STOP_SEED:
            return self.updateStopSeed(req)
        elif opc == p.OPT_UPLOAD_FILE: #upload new file --> create new torrent object
            return self.addNewFile(req)
        else:                   #invalid opc
            return p.RET_FAIL # possibly p.RET_FAIL?
    
    def getTorrentDict(self):                   #res opcode=1
        responseDict = {
            'torrentList': self.torrent,
            'opc': p.OPT_RES_LIST
        }
        return responseDict
    
    def getTorrentObject(self, req: dict):      #res opcode=2
        responseDict = {
            'opc': p.OPT_RES_OBJ,
            'res': True                     #to tell client that the torrent object exists
        }
        if req['tid'] not in self.torrent:  #torrent object does not exist in list
            responseDict['res'] = False
            return responseDict                    
        myTorrentObj = self.torrent[ req['tid'] ]
        responseDict['torrentObj'] = myTorrentObj                   #TODO: Do we want to add the peer list with the torrent object?

        torr_peers = []
        for key, value in self.peers.items():                 #obtain all peers who are in that torrent as a list of dict
            if (value['tid'] == req['tid']):
                torr_peers.append(value)          #TODO: A list of dictionaries isn't working
        responseDict['peers'] = torr_peers

        newPeer = {                             #adds new peer into peer list
            'ip': req['ip_address'],
            'status':  'leecher',
            'tid': req['tid'],
            'port': req['port'],
            'pieces': 0
        }
        self.peers[req['pid']] = newPeer    
        return responseDict

    def updatePeerStatus(self, req:dict):
        if req['pid'] not in self.peers:
            return p.RET_FAIL
        self.peers[ req['pid'] ]['status'] = 'seed'         #change peer status to seeder
        self.peers[ req['pid'] ]['n_pieces']  = self.torrent[req['tid'] ].pieces
        return p.RET_SUCCESS

    def updateStopSeed(self, req: dict): 
        if req['pid'] not in self.peers:
            return p.RET_FAIL
        self.peers[ req['pid'] ]['status'] = 'None'     
        return p.RET_SUCCESS

    def addNewFile(self, req: dict):            
        myTorrent = Torrent(req['filename'])        #create the torrent object
        self.torrent[self.nextTorrentId] = myTorrent    #insert into torrent dictionary
        print(myTorrent.filename)
        newPeer = {
            'ip': req['ip_address'],
            'status':  'hello',
            'tid': self.nextTorrentId,
            'port': req['port'],
            'pieces': req['pieces']
        }
        self.nextTorrentId+=1
        self.peers[req['pid']] = newPeer            #insert peer into peerlist
        return p.RET_SUCCESS
    
    
    async def handleRequest(self, reader, writer):
        # TODO: 200 is the current constant, what is max req payload size?
        try:
            data = await reader.read(200)
        
            message = json.loads(data.decode())
            addr = writer.get_extra_info('peername')

            print(f"\n[TRACKER] Debug: received {message!r} from {addr!r}.")

            payload = self.receiveRequest(message)

            # TODO: this CANNOT differentiate from torrent_list vs torrent_obj
            response = {}

            if type(payload) is dict:
                response.update({"opt": p.RET_SUCCESS})
                response.update({"torrent_list": payload})

            # TO CONSIDER: receiveRequest(...) only returns 0/1 or [torrent_list, torrent_obj]
            else:
                response.update({"opt": payload})

            jsonResponse = json.dumps(response)
            writer.write(jsonResponse.encode())
            await writer.drain()
            print("[TRACKER] Closing the connection for", addr)
        except:
            print("[TRACKER] Peer", writer.get_extra_info('peername'), "has disconnected.")
            
        writer.close()

async def main():
    ip = "127.0.0.1"
    port = 8888
    
    t = TrackerServer()
    server = await asyncio.start_server(t.handleRequest, ip, port)
    addr = server.sockets[0].getsockname()
    print(f'[TRACKER] Serving on {addr}')

    async with server:
        await server.serve_forever()

asyncio.run(main())