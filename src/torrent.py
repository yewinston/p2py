from protocol import *

class Torrent:
    def __init__(self, tid, filename, numPieces):
        self.tid = tid
        self.filename = filename
        self.pieces = numPieces
        self.seeders = dict()
        self.leechers = dict()
    
    def addSeeder(self, pid: str, peer_ip, peer_port):
        newSeeder = dict()
        newSeeder[IP] = peer_ip
        newSeeder[PORT] = peer_port
        self.seeders[pid] = newSeeder

    def removeSeeder(self, pid: str):
        if pid in self.seeders:
            del self.seeders[pid]

    def addLeecher(self, pid: int, peer_ip, peer_port):
        newLeecher = dict()
        newLeecher[IP] = peer_ip
        newLeecher[PORT] = peer_port
        self.leechers[pid] = newLeecher

    def removeLeecher(self, pid: str):
        if pid in self.leechers:
            del self.leechers[pid]
    
    def getSeeders(self) -> dict():
        return self.seeders

    def getLeechers(self) -> dict():
        return self.leechers
        