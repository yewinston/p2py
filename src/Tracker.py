from bencode import *
from torrent import *
# FIXME: would p be confusing for peer?
import protocol as p
import asyncio
import json

class TrackerServer:                              
    #torrent metadata
    def __init__(self):
        self.nextTorrentId = 0 
        self.torrent = {}              #the torrent list (dictionary), defined by its unique torrentID

    def handleRequest(self, req):
        opc = req.get('OPC')
        response = {"OPC": opc}
        
        if opc == p.OPT_GET_LIST:
            torrent_list = self.getTorrentDict()
            if torrent_list:
                response.update({"torrent_list": self.getTorrentDict()})
                response.update({ "RET": p.OPT_RES_LIST })
            else:
                response.update({ "RET": p.RET_FAIL })

        elif opc == p.OPT_GET_TORRENT:
            torrent_obj = self.getTorrentObject(req)
            if torrent_obj:
                response.update({"torrent_obj": torrent_obj})
                response.update({ "RET": p.OPT_RES_OBJ })
            else:
                response.update({ "RET": p.RET_FAIL })

        elif opc == p.OPT_START_SEED:
            response.update({"RET": self.updatePeerStatus(req)})

        elif opc == p.OPT_STOP_SEED:
            response.update({"RET": self.updateStopSeed(req)})

        elif opc == p.OPT_UPLOAD_FILE: #upload new file --> create new torrent object
            response.update({"RET": self.addNewFile(req)})

        else:                   #invalid opc
            response.update({ "RET": p.RET_FAIL })

        return response
    
    def getTorrentDict(self):                   #res opcode=1
        responseDict = {
            'torrentList': self.torrent,            #THIS WILL BE RETURNED AS A DICT: DICT
            'opc': p.OPT_RES_LIST,
            'res': p.RET_SUCCESS
        }
        return responseDict
    
    def getTorrentObject(self, req: dict):      #res opcode=2
        responseDict = {
            'opc': p.OPT_RES_OBJ,
            'res': p.RET_SUCCESS                    #to tell client that the torrent object exists
        }
        if req['tid'] not in self.torrent:  #torrent object does not exist in list
            responseDict['res'] = p.RET_FAIL
            return responseDict                    
        myTorrentObj = self.torrent[ req['tid'] ]
        responseDict['torrentObj'] = myTorrentObj                 
        self.torrent[req['tid'] ].addPeer(req, 'leecher')                    #add peer into torrent object      
        return responseDict

    def updatePeerStatus(self, req:dict):
        responseDict = {
            'opc': p.OPT_START_SEED,
            'res': p.RET_SUCCESS
        }
        if req['tid'] not in self.torrent:
            responseDict['res'] = p.RET_FAIL
            return responseDict
        self.torrent[ req['tid'] ].updatePeer(req, 'seeder')
        return responseDict

    def updateStopSeed(self, req: dict): 
        responseDict = {
            'opc': p.OPT_STOP_SEED,
            'res': p.RET_SUCCESS
        }
        if req['tid'] not in self.torrent:
            responseDict['res'] = p.RET_FAIL
            return responseDict
        self.torrent[req['tid'] ].updatePeer(req, 'None')   
        return responseDict

    def addNewFile(self, req: dict):
        responseDict = {
            'opc': p.OPT_UPLOAD_FILE,
            'res': p.RET_SUCCESS
        }
        try:                    
            myTorrent = Torrent(req['filename'])        #create the torrent object
            myTorrent.addPeer(req, 'seeder')                      #add peer the seeder into torrent object   
            self.torrent[self.nextTorrentId] = myTorrent    #insert into torrent dictionary
            self.nextTorrentId+=1
        except:
            responseDict['res'] = p.RET_FAIL
        return responseDict
    
    async def receiveRequest(self, reader, writer):
        '''
            Take in the client request
            It will call handleRequest -> give it a response object {"OPT": __, "RET": __, "payload": __ }
            receiveRequest will send this ---^ response object
        '''
        # TODO: 200 is the current constant, what is max req request size?
        try:
            data = await reader.read(200)
        
            cliRequest = json.loads(data.decode())
            addr = writer.get_extra_info('peername')

            print(f"\n[TRACKER] Debug received {cliRequest!r} from {addr!r}.")
            
            # TO CONSIDER: handleRequest(...) only returns 0/1 or [torrent_list, torrent_obj]
            response = self.handleRequest(cliRequest)

            # Send payload response to client
            payload = json.dumps(response)
            print("[TRACKER] Debug send payload:", payload)
            writer.write(payload.encode())
            
            await writer.drain()
            print("[TRACKER] Closing the connection for", addr)
        except:
            print("[TRACKER] Peer", writer.get_extra_info('peername'), "has disconnected.")

        writer.close()

async def main():
    ip = "127.0.0.1"
    port = 8888
    
    t = TrackerServer()
    server = await asyncio.start_server(t.receiveRequest, ip, port)
    addr = server.sockets[0].getsockname()
    print(f'[TRACKER] Serving on {addr}')

    async with server:
        await server.serve_forever()

asyncio.run(main())