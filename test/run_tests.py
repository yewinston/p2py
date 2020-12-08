from src.client import *
from src.Tracker import *

def test_createServerRequest():
    # sample :
    cli = Client('127.0.0.1', '8080')
    payload = cli.createServerRequest(opc=10)
    assert(payload)
    print('todo')

def test_createPeerRequest():
    print('todo')

def test_createPeerResponse():
    print('todo')

def test_setPieceBuffer():
    print('todo')

def test_createServerResponse():
    print('todo')

def test_createNewTorrent():
    print('todo')
    


