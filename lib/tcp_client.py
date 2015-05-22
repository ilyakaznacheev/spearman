import socket
import struct
from Queue import Queue

FRAME_TIME_MASK = "h"*8


class TCPCLient(object):
    """
    Simple TCP client
    for work with NMCServer

    public methods:
    - init - set socket connection defaults
    - connect - initiate socket connection
    - register_client - send client name to NMCServer
    - get_next - receive one data package from server
    - disconnect - interrupts socket connection
    """

    CLIENT_NAME = "Spearman"
    CLIENTS = dict()
    POLL = 0x7FFFFFFF
    MAX_TCP_SIZE = 2**16

    def __init__(self, host, port, clients=CLIENTS):
        self.hpdata = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.formatter = HEXFormatter()
        self.clients = clients

    def connect(self):
        """ connect to NMCServer """
        try:
            self.socket.connect(self.hpdata)
        except socket.error:
            return False
        else:
            return True

    def disconnect(self):
        """ disconnect from NMCServer """
        self.socket.close()

    def register_client(self, client_name=CLIENT_NAME):
        """ register on NMCServer as <client_name> """
        uni_client_name = self.formatter.prepare_uni_string(client_name)
        string = self.formatter.encode_str('i', len(uni_client_name)/2)
        self._send(string)

        string = self.formatter.encode_str(
            '{}s'.format(len(uni_client_name)), uni_client_name
            )
        self._send(string)

    def get_next(self):
        """ receive and prepare next data package """
        while True:
            rcv = self._receive()
            result = self._deal_with_recv_data(rcv)
            if result:
                return result

    def _send(self, data_string):
        """ send some data via tcp """
        self.socket.sendall(data_string)

    def _receive(self):
        """ receive some data via tcp """
        received_data = self.socket.recv(self.MAX_TCP_SIZE)

        return received_data

    def _deal_with_recv_data(self, data):
        """ separate server's and clients' commands """
        command = self.formatter.decode_str('i', data[:4])
        if command:
            result = self._client_command(data[4:])
        else:
            result = self._server_command(data[4:])

        return result

    def _add_client(self, data):
        """ add an info about new client: number and name """
        client = self._get_client_data(data)

        self.clients[client[0]] = client[1]

    def _remove_client(self, data):
        """ remove disconnected client from client list """
        client = self._get_client_data(data)

        del self.clients[client[0]]

    def _get_client_data(self, data):
        """ parse client data """
        client_num = self.formatter.decode_str('i', data[:4])
        name_len = self.formatter.decode_str('i', data[4:8])
        client_name = self.formatter.decode_str(
            '{}s'.format(name_len*2), data[8:]
            )

        return (client_num, client_name)

    def _server_command(self, data):
        """ process server's command """
        command = self.formatter.decode_str('i', data[:4])
        if not command:
            self.disconnect()
        elif command == self.POLL:
            pass
        elif command == 1:
            self._add_client(data[4:])
        elif command == -1:
            self._remove_client(data[4:])

    def _client_command(self, data):
        """ process client's command """
        msg_len = self.formatter.decode_str('i', data[:4])
        return data[4:msg_len+4]


class HEXFormatter(object):
    """
    Socket IO formetter

    public methods:
    - encode_str - encode data to hexadecimal representation
    - decode_str - decode hexadecimal string to inner data formats
    - prepare_uni_string - translate unicode string to hexadecimal
                           representation without u-sign
    """

    def encode_str(self, mask, *values):
        """
        encodes a list of values to
        hexadecimal string
        input:
        - mask - string packing mask
        - values - list of any data
        output:
        - string of hexadecimal data
        """
        result = struct.pack(mask, *values)

        return result

    def decode_str(self, mask, string):
        """
        decodes a hexadecimal string
        to list of values
        input:
        - mask - string packing mask
        - string - string of hexadecimal data
        output:
        - list (or one value) of converted data
        """
        result = struct.unpack(mask, string)

        if len(result) == 1:
            return result[0]
        else:
            return result

    def prepare_uni_string(self, string):
        return string.encode("utf-16")[2:]


class SpearmanSocketListener(object):
    """
    Simple socket client
    """
    ARRAYS_NUMBER = 29
    ARRAY_ELEMENTS = 24
    TIME_MASK = "hhhhhhhh"
    ARRAY_MASK = 'h'*ARRAYS_NUMBER*ARRAY_ELEMENTS
    FRAME_TYPE = 6

    def __init__(self, host, port):
        self.tcp_client = TCPCLient(host, port)
        self.formatter = HEXFormatter()
        self.que = Queue()

    def connect(self):
        return self.tcp_client.connect()

    def register(self):
        self.tcp_client.register_client()

    def disconnect(self):
        self.tcp_client.disconnect()

    def read_frame(self):
        """ read frame according some weird frame format """
        while True:
            raw_data = self.tcp_client.get_next()
            if self.formatter.decode_str('i', raw_data[:4]) == self.FRAME_TYPE:
                break

        time_begin = self.formatter.decode_str(self.TIME_MASK, raw_data[4:20])
        time_end = self.formatter.decode_str(self.TIME_MASK, raw_data[20:36])
        # reserved = raw_data[36:64]
        discret_friq = raw_data[64:68]
        message = raw_data[68:]
        raw_array = self.formatter.decode_str(self.ARRAY_MASK, message)

        arrays = list(self._chunks(raw_array, self.ARRAY_ELEMENTS))
        transponated = zip(*arrays)
        return transponated, time_begin, time_end, discret_friq

    def _chunks(self, l, n):
        """ slice list to N parts """
        for i in xrange(0, len(l), n):
            yield l[i:i+n]

    def get(self):
        """
        get next line from a queue if it is full,
        overwise receive data from server and
        fill queue with perpared server data
        """
        if self.que.empty():
            self._fill_queue()

        next_line = self.que.get()
        return next_line

    def _fill_queue(self):
        """ add new lines from received packages """
        result = self.read_frame()[0]
        for line in result:
            self.que.put(line)


def main():
    host = "192.168.0.105"
    port = 8000
    listener = SpearmanSocketListener(host, port)
    listener.connect()
    listener.register()

    while True:
        result = listener.get()
        if not result:
            break
        else:
            print(result)

    listener.disconnect()


if __name__ == '__main__':
    main()
