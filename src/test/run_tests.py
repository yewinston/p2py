from src.client import *
from src.Tracker import *
from src.protocol import *

def test_createServerRequest():
    ip = '127.0.0.2'
    port = '8080'
    cli = Client(ip, port)
    peer_id = cli.createPeerID()
    opc = 11
    tid = 0
    expectedPayload = {
        OPC:opc,
        IP:ip,
        PORT:port,
        PID:peer_id,
        TID:tid
    }
    actualPayload = cli.createServerRequest(opc=opc, torrent_id=tid)
    assert(actualPayload == expectedPayload )

def test_handleServerRequest():
    tracker = TrackerServer()
    opc = OPT_GET_LIST
    ip = '127.0.0.2'
    port = '8080'
    peer_id = 'test'
    tid = 0
    requestPayload = {
        OPC:opc,
        IP:ip,
        PORT:port,
        PID:peer_id,
        TID:tid
    }
    expectedPayload = {
        OPC: opc,
        RET: RET_NO_AVAILABLE_TORRENTS
    }
    actualPayload = tracker.handleRequest(requestPayload)

def test_createPeerRequest():
    ip = '127.0.0.2'
    port = '8080'
    cli = Client(ip, port)
    opc = OPT_GET_PIECE
    piece_idx = 0
    expectedPayload = {
        OPC:opc,
        IP:ip,
        PORT:port,
        PIECE_IDX: piece_idx
    }
    actualPayload = cli.createPeerRequest(opc=opc, piece_idx=piece_idx)
    assert(actualPayload == expectedPayload )

def test_handlePeerRequest():
    ip = '127.0.0.2'
    port = '8080'
    cli = Client(ip, port)
    opc = OPT_GET_PEERS
    requestPayload = {
        OPC:opc,
        IP:ip,
        PORT:port,
    }
    expectedResponse = {
        OPC:opc,
        IP:ip,
        PORT:port,
        PEER_LIST: {},
        RET: 0
    }
    actualResponse = cli.handlePeerRequest(requestPayload)
    assert(actualResponse == expectedResponse)



