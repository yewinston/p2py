from src.client import *

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

def test_createServerResponse():
    print('todo')


