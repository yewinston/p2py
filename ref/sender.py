from socket import *
import random
import sys
import json
import time

def setRandomSeeds(timing, corrupt, data):
    rand_timing = random.Random()
    rand_timing.seed(timing)

    rand_corrupt = random.Random()
    rand_corrupt.seed(corrupt)

    rand_data = random.Random()
    rand_data.seed(data)

    return rand_timing, rand_corrupt, rand_data

def getRandomValue(randomType, rand):
#    Returns a random value based on the randomType indicated
#    0/Timing = [0,5]
#    1/Corrupt = [0,1)
#    2/Data = [0, 1024]

    if randomType == 0:
        return rand.uniform(0, 5)
    elif randomType == 1:
        return rand.random()
    elif randomType == 2:
        return rand.randint(0, 1024)


# Packet is [data, seq#, ack#, isAck] 1 if true, 0 if false.
def make_pkt(data, seqSeg, seqAck, isAck):
    packet = {"data": data, "seqSeg": seqSeg, "seqAck": seqAck, "isAck": isAck}
    return json.dumps(packet)

def unpack_ack(ackString):
    ack = json.loads(ackString)
    return ack

def main():
    """
    [1] Seed for Timing 
    [2] Num of Packets
    [3] Seed for ACK corrupt 
    [4] P-value for corrupt [0, 1)
    [5] Seed for data 
    [6] Round trip travel time 
    """

    print("Enter random number generator seed for timing")
    timing_seed = int(input())
    print("Enter number of segments to send")
    numOfPackets = int(input())
    print("Enter random number generator seed for ACK corruption")
    corrupt_seed = int(input())
    print("Enter probability [0,1) for corrupted ACKs")
    corrupt_p = float(input())
    print("Enter random number generator seed for data")
    data_seed = int(input())
    print("Enter round trip travel time (seconds)")
    roundTripTime = float(input())
    
    ## Set up connection
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientPort = 2048
    serverName = 'localhost'
    serverPort = 50007
    clientSocket.connect((serverName, serverPort))
    clientSocket.settimeout(roundTripTime)

    ## Set random seeds
    rand_timing, rand_corrupt, rand_data = setRandomSeeds(float(timing_seed), float(corrupt_seed), float(data_seed))

    ## Initialize Packet Data
    sequenceNum = True
    ackNum = False
    isAck = True
    nextSendTime = 0

    print("\nEstablishing connection . . .\n")
    for i in range(numOfPackets):
        packetData = getRandomValue(2, rand_data)
        sequenceNum = False if sequenceNum else True
        elapsedTime = time.time()
        nextSendTime = nextSendTime + elapsedTime

        print("WAIT FOR CALL", int(sequenceNum), "FROM ABOVE\n")

        # WAIT TO SEND BASED ON ELAPSED TIME
        if (elapsedTime < nextSendTime):
            time.sleep(nextSendTime - elapsedTime)
        nextSendTime = getRandomValue(0, rand_timing)

        # RDT_SEND
        packet = make_pkt(packetData, sequenceNum, ackNum, isAck)
        print("A data segment with sequence number", int(sequenceNum), "is about to be sent")

        # UDT_SEND(sndpkt)
        clientSocket.send(packet.encode())
        print("Segment sent: data =", packetData, "seqSeg =", int(sequenceNum), "seqAck =", int(ackNum), "isack =", int(isAck), "\n")

        print("The sender is moving to state WAIT FOR ACK", int(sequenceNum), "\n")

        # If we havent' received a response for RTT... then we must resend.
        
        # RDT_RCV(rcvpkt) 
        try:
            ack = unpack_ack(clientSocket.recvfrom(clientPort)[0].decode())
        except:
            ack = None

        # COMPUTE IF ACK IS CORRUPTED
        ackIsCorrupt = True if getRandomValue(1, rand_corrupt) < corrupt_p else False

        while(ack == None or ackIsCorrupt or ack["isAck"] == False or ack["seqAck"] != sequenceNum):
            if (ack == None):
                print("Timedout. No ack was received\n")
            else:
                print("A Corrupted ACK segment has just been received\n")

            print("A data segment with sequence number", int(sequenceNum), "is about to be resent")
            print("Segment sent: data =", packetData, "seqSeg =", int(sequenceNum), "seqAck =", int(ackNum), "isack =", int(isAck), "\n")
            clientSocket.send(packet.encode())

            print("The sender is moving back to state WAIT FOR ACK", int(sequenceNum), "\n")
            try:
                ack = unpack_ack(clientSocket.recvfrom(clientPort)[0].decode())
            except:
                ack = None

            # Assuming it can be corrupted again..
            ackIsCorrupt = True if getRandomValue(1, rand_corrupt) < corrupt_p else False



        print("An ACK", int(ack["seqAck"]), "segment has just been received")
        print("ACK received: data =", ack["data"], "seqSeg =", int(ack["seqSeg"]), "seqAck =", int(ack["seqAck"]), "isAck =", int(ack["isAck"]), "\n")
    
    print("Closing connection . . .")
    clientSocket.send(("close").encode())
    clientSocket.close()

if __name__ == '__main__':
    main()