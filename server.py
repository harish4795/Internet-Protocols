# Python file to implement the Point to Multipoint Server (Receiver)

# Created for CSC573 - Internet Protocols Project-2 by akrish12 and hpalani


import socket
import sys
from random import *

serverPort = int(sys.argv[1])      # Getting ServerPort, Filename and Probability value
file_recv = sys.argv[2]
p = float(sys.argv[3])
MSS = 556
print('Server is up and running')
seqno_server = 0
ackPacket = '1010101010101010'
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind(('', serverPort))
file = open(file_recv+'.txt', 'w')


# Citation: http://stackoverflow.com/questions/1767910/checksum-udp-calculation-python
# Function to calculate checksum
def add_carry(x, y):
    z = x + y
    return (z & 0xffff) + (z >> 16)


def checksum(msg):
    if (len(msg) % 2) != 0:
        msg += "0".encode('utf-8')

    s = 0
    for i in range(0, len(msg), 2):
        w = msg[i] + ((msg[i+1]) << 8)
        s = add_carry(s, w)
    return ~s & 0xffff


data, address = serverSocket.recvfrom(MSS)
seqno_client = int(data[0:32], 2)
checksum_client = int(data[32:48], 2)
checksum_prev = 0
seqno_prev = 0
message = data[64:]
if seqno_server == seqno_client:                # Sequence number starts with zero
    r = random()                                # To produce 0 to 1 values
    if r > p:
        checksum_server = checksum(message)         # For the first segment this block is executed
        if checksum_client == checksum_server:
            segment_num = '{0:032b}'.format(seqno_server)
            send_ack = segment_num + '{0:016b}'.format(0) + ackPacket
            serverSocket.sendto(send_ack.encode('utf-8'), address)
            file.write(message.decode('utf-8'))
            if seqno_server == 1:
                seqno_server = 0
            else:
                seqno_server += 1                   # Next segments it expects 1
    else:
        print('Packet loss, sequence number = ', seqno_server)


while(data):

    data, address = serverSocket.recvfrom(MSS)
    seqno_client = int(data[0:32], 2)
    checksum_client = int(data[32:48], 2)
    message = data[64:]
    if message.decode('utf-8') == '':
        serverSocket.sendto("Last segment".encode('utf-8'), address)
        file.write(message.decode('utf-8'))
        break
    else:
        if seqno_server == seqno_client:        # To check whether client has received ack from server otherwise re transmit
            r = random()
            if r > p:                                               # For all following segments
                checksum_server = checksum(message)
                checksum_prev = checksum_server
                if checksum_client == checksum_server:
                    segment_num = '{0:032b}'.format(seqno_server)
                    send_ack = segment_num + '{0:016b}'.format(0) + ackPacket
                    serverSocket.sendto(send_ack.encode('utf-8'), address)
                    file.write(message.decode('utf-8'))
                    if seqno_server == 1:
                        seqno_prev = 1
                        seqno_server = 0
                    else:
                        seqno_prev = 0
                        seqno_server += 1
                else:
                    continue
            else:
                print('Packet loss, sequence number = ', seqno_server)
        else:
            if checksum_client == checksum_prev:                        # Checksum should be same for client and server
                segment_num = '{0:032b}'.format(seqno_prev)
                send_ack = segment_num + '{0:016b}'.format(0) + ackPacket
                serverSocket.sendto(send_ack.encode('utf-8'), address)


file.close()
print('Successful Transfer')
serverSocket.close()
