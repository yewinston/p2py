from bencode import *
from torrent import *

class TrackerServer:                              
    #torrent metadata
    def __init__(self):
        self.nextTorrentId = 1 
        self.torrent = {}              #the torrent list (dictionary), defined by its unique torrentID
        self.peers = {}                #distingueshed by peerId, value will be a dictionary that holds that user's information 

    def receiveRequest(self, req: dict):          #the things that will be returned will be in dict form
        if req['OPC'] == 1:
            return self.getTorrentDict()
        
        elif req['OPC'] == 2:
            return self.getTorrentObject(req)
        elif req['OPC'] ==3:
            return self.updatePeerStatus(req)
        elif req['OPC']==4:
            return self.updateStopSeed(req)
        elif req['OPC'] ==5: #upload new file --> create new torrent object
            return self.addNewFile(req)
        elif req['OPC'] == 6:               #user selects a specific tid to be part of
            return self.addPeer(req)
        else:                   #invalid OPC
            return None
    
    def getTorrentDict(self):
        responseDict = {'torrentList': self.torrent}
        return responseDict
    
    def getTorrentObject(self, req: dict):
        if req['tid'] not in self.torrent:  #torrent object does not exist in list
            return None
        myTorrentObj = self.torrent[ req['tid'] ]
        responseDict = {'torrentObj': myTorrentObj}
        return responseDict

    def updatePeerStatus(self, req:dict):
        if req['pid'] not in self.peers:
            return None
        self.peers[ req['pid'] ]['status'] = 'seed'         #change peer status to seeder
        #self.peers[ req['pid'] ]['n_pieces']  =            #TODO: update set pieces, have to create torrent obj first
        return 1

    def updateStopSeed(self, req: dict):
        if req['pid'] not in self.peers:
            return None
        self.peers[ req['pid'] ]['status'] = 'None'        #Removes role as seeder
        return 1

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
        return 1
    
    def addPeer(self, req: dict):
        flag = True
        if req['tid'] not in self.torrent:
            return None
        newPeer = {
            'ip': req['ip_address'],
            'status':  'leecher',
            'tid': req['tid'],
            'port': req['port'],
            'pieces': 0
        }
        self.peers[req['pid']] = newPeer            #insert peer into peerlist
        return 1


                                            