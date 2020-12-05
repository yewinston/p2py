

#Todo: create the Torrent object
class Torrent:
    def __init__(self, filename):
        self.filename = filename
        self.pieces = 5
        self.peers = {}
        return
    

    def addPeer(self, req: dict, status):
        newPeer = {
            'ip': req['ip_address'],
            'status':  status,
            'port': req['port'],
        }
        if status=='seeder':                           # TODO: THIS WILL NEED TO CHANGE
            newPeer['pieces'] = req['pieces']         #change peer status to seeder
        else :
            newPeer['pieces'] = 0
        self.peers[req['pid'] ] = newPeer            #insert peer into peerlist
    
    def updatePeer(self, req: dict, status):
        try:
            self.peers[req['pid'] ]['status'] = status
            if (status=='seeder'):
                self.peers[req['pid'] ]['pieces'] = self.pieces
        except:
            print("Peer has failed to be updated")
    
    def getPeerList(self):
        return self.peers
        
    