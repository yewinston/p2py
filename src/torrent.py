from protocol import *

#Todo: create the Torrent object
class Torrent:
    def __init__(self, tid, filename, numPieces):
        self.tid = tid
        self.filename = filename
        self.pieces = numPieces
        self.seeders = {}
        self.leechers = {}
        return
    
    def addSeeder(self, pid: str, peer_ip, peer_port):
        newSeeder = {
            PID: pid,
            IP: peer_ip,
            PORT: peer_port
        }
        self.seeders.update({PID: newSeeder})

    def removeSeeder(self, pid: str):
        if pid in self.seeders:
            del self.seeders[pid]

    def addLeecher(self, pid: int, peer_ip, peer_port):
        newLeecher = {
            PID: pid,
            IP: peer_ip,
            PORT: peer_port
        }
        self.leechers.update({PID: newLeecher})

    def removeLeecher(self, pid: str):
        if pid in self.leechers:
            del self.leechers[pid]
    
    def getSeederList(self) -> dict():
        return self.seeders

    def getLeecher(self) -> dict():
        return self.leechers
        