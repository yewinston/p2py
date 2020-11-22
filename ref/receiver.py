from socket import *
import random
import sys
import json

def make_ack(data, seqSeg, seqAck, isAck):
    ack = {"data": data, "seqSeg": seqSeg, "seqAck": seqAck, "isAck": isAck}
    return json.dumps(ack)

def unpack_pkt(pktString):
    return json.loads(pktString)

def main():
    """
    [1] Seed for data segment is corrupted
    [2] P-value for data corrupt [0, 1)
    """

    #inputs = sys.argv
    #corrupt_seed = inputs[1]
    #corrupt_p = inputs[2]

    print("Enter random number generator seed for segment corruption")
    corrupt_seed = int(input())
    print("Enter probability [0,1) for corrupted segments")
    corrupt_p = float(input())

    ## Set up connection
    print("\nEstablishing connection . . .\n")
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverName = 'localhost'
    serverPort = 50007
    clientPort = 2048
    serverSocket.bind((serverName, serverPort))
    serverSocket.listen()
    serverId = serverSocket.accept()[0]

    # Set random seed
    rand_corrupt = random.Random()
    rand_corrupt.seed(corrupt_seed)

    # Initialize Ack Data
    data = 0
    sequenceNum = False
    ackNum = True
    isAck = True
    lastSequenceNum = None

    stateString = "The receiver is moving to state WAIT FOR"
    while True:
        ackNum = False if ackNum else True

        # RDT_RCV
        pktString = serverId.recvfrom(clientPort)[0].decode()
        if (pktString == "close"):
            print("Closing connection . . .")
            break
        packet = unpack_pkt(pktString)
        #print("The receiver is moving to state WAIT FOR", ackNum, "FROM BELOW")
        print(stateString, int(ackNum),  "FROM BELOW\n")

        # COMPUTE IF DATA IS CORRUPTED
        pktIsCorrupt = True if rand_corrupt.random() < corrupt_p else False

        while(pktIsCorrupt):
            print("A Corrupted segment has been received\n")
            print("The receiver is moving back to state WAIT FOR", int(ackNum),  "FROM BELOW\n")
            packet = unpack_pkt(serverId.recvfrom(clientPort)[0].decode())
            pktIsCorrupt = True if rand_corrupt.random() < corrupt_p else False
            

        if (packet["seqSeg"] == lastSequenceNum):
            print("A duplicate segment with sequence number", int(packet["seqSeg"]), "has been received")
            ackNum = False if ackNum else True
            stateString = "The receiver is moving back to state WAIT FOR"
        else:
            print("A segment with sequence number", int(packet["seqSeg"]), "has been received")
            lastSequenceNum = packet["seqSeg"]
            stateString = "The receiver is moving to state WAIT FOR"

        print("Segment received contains: data =", packet["data"], "seqSeg =", int(packet["seqSeg"]), "seqAck =", int(packet["seqAck"]), "isAck =", int(packet["isAck"]))

        # UDT_SEND(sndack)
        ack = make_ack(data, sequenceNum, ackNum, isAck)
        print("An ACK", int(packet["seqSeg"]), "is about to be sent")

        serverId.send(ack.encode())
        print("ACK to send contains: data =", data, "seqSeg =", int(sequenceNum), "seqAck =", int(ackNum), "isAck =", int(isAck), "\n")
    
    serverId.close()
        

if __name__ == '__main__':
    main()