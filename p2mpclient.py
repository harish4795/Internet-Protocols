# Python file to implement the Point to Multipoint Client (Sender)

# Created for CSC573 - Internet Protocols Project-2 by akrish12 and hpalani

import threading
import datetime
import socket
import sys
import os

header_size = 8
buffer_size = 1
location = "D:\\Grad\\IP 573\\Project\\Project 2"
argument_size = len(sys.argv)
server_port = int(sys.argv[argument_size-3])
MSS = int(sys.argv[argument_size-1]) - header_size
server_ip_address = []
client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
file = sys.argv[argument_size-2]
dataPacket = '0101010101010101'
data = ''

for i in range(1, argument_size-3):
    server_ip_address.append(sys.argv[i])


def rdt_send(offset_num):
    f = open(location+'\\'+file+'.txt', 'rb')
    f.seek(offset_num)
    leng = f.read(buffer_size)
    if leng:
        return leng
    else:
        return b''
    f.close()


# Function to calculate checksum
def add_carry(x, y):
    z = x + y
    return (z & 0xffff) + (z >> 16)


# Citation: http://stackoverflow.com/questions/1767910/checksum-udp-calculation-python
def checksum(msg):
    if (len(msg) % 2) != 0:
        msg += "0".encode('utf-8')

    s = 0
    for i in range(0, len(msg), 2):
        w = msg[i] + ((msg[i+1]) << 8)
        s = add_carry(s, w)
    return ~s & 0xffff


class serverThread(threading.Thread):

    def __init__(self, data, server_address):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.server_address = server_address
        self.data = data

    def run(self):
        client_sock.sendto(self.data, self.server_address)


thread_list = []
size_file = os.stat(location+'\\'+file+'.txt').st_size
rem_size = size_file
count = 0
segment_num = 0
offset_num = 0
start = datetime.datetime.now()

while(rem_size>=0):
    list_ack = list(server_ip_address)
    ack_count = 0
    buffer_temp = b''
    print('Remaining size:', rem_size)

    while(len(buffer_temp) <= MSS):
        temp = rdt_send(offset_num)

        if((len(temp)==1) and (len(buffer_temp)<MSS)):
            buffer_temp = buffer_temp.__add__(temp)

        elif((len(temp) < 1) and (len(buffer_temp) < MSS)):
            buffer_temp.__add__(temp)
            segment_num_bin = '{0:032b}'.format(segment_num)
            check_sum = checksum(buffer_temp)
            binary_value_check = '{0:016b}'.format(check_sum)
            data = segment_num_bin.encode('utf-8') + binary_value_check.encode('utf-8') + dataPacket.encode('utf-8') + buffer_temp
            count += 1
            for ip_address in server_ip_address:
                server_address = (ip_address, server_port)
                new_thread = serverThread(data, server_address)
                new_thread.start()
                thread_list.append(new_thread)
            for t in thread_list:
                t.join()

            while(ack_count != len(server_ip_address)):
                client_sock.settimeout(0.05)
                try:
                    ack, address = client_sock.recvfrom(MSS)
                    server_seq_num = int(ack[0:32], 2)
                    if server_seq_num == segment_num:
                        if address[0] in list_ack:
                            ack_count += 1
                            list_ack.remove(address[0])

                except socket.timeout:
                    print('Timeout, sequence number = ', segment_num)
                    for ip_address in list_ack:
                        server_address = (ip_address, server_port)
                        new_thread = serverThread(data, server_address)
                        new_thread.start()
                        thread_list.append(new_thread)
                    for t in thread_list:
                        t.join()
                    continue

            st = ''
            segment_num_bin = '{0:032b}'.format(segment_num)
            binary_value_check = '{0:016b}'.format(0)
            data = segment_num_bin.encode('utf-8') + binary_value_check.encode('utf-8') + dataPacket.encode('utf-8') + st.encode('utf-8')
            for ip_address in server_ip_address:
                server_address = (ip_address, server_port)
                new_thread = serverThread(data, server_address)
                new_thread.start()
                thread_list.append(new_thread)
            for t in thread_list:
                t.join()
            break
        else:
            break

        offset_num = offset_num + buffer_size
        if((len(temp)==1) and (len(buffer_temp) == MSS)):
            segment_num_bin = '{0:032b}'.format(segment_num)
            check = checksum(buffer_temp)
            binary_value_check = '{0:016b}'.format(check)
            data = segment_num_bin.encode('utf-8') + binary_value_check.encode('utf-8') + dataPacket.encode('utf-8') + buffer_temp
            count += 1
            for ip_address in server_ip_address:
                server_address = (ip_address, server_port)
                new_thread = serverThread(data, server_address)
                new_thread.start()
                thread_list.append(new_thread)
            for t in thread_list:
                t.join()

            while(ack_count != len(server_ip_address)):
                client_sock.settimeout(0.05)

                try:
                    ack, address = client_sock.recvfrom(MSS)
                    server_seq_num = int(ack[0:32], 2)
                    if server_seq_num == segment_num:
                        if address[0] in list_ack:
                            list_ack.remove(address[0])
                            ack_count += 1

                except socket.timeout:
                    print('Timeout, sequence number = ', segment_num)
                    for ip_address in list_ack:
                        server_address = (ip_address, server_port)
                        new_thread = serverThread(data, server_address)
                        new_thread.start()
                        thread_list.append(new_thread)
                    for t in thread_list:
                        t.join()
                    continue

    if segment_num == 1:
        segment_num = 0
    else:
        segment_num += 1
    rem_size = rem_size - MSS

end = datetime.datetime.now()
print('Time taken: ', (end-start))