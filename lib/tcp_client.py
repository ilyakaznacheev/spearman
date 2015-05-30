import socket
import struct
from Queue import Queue
from Queue import Empty as QueueEmpty
import time
import multiprocessing as mp

import errors

COMMAND_CONNECT = "connect"
COMMAND_REGISTER = "register"
COMMAND_DISCONNECT = "disconnect"


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
        print("\nserver command: {}".format(command))
        if not command:
            self.disconnect()
            raise errors.TCPErrorServerDisconnect()
        elif command == self.POLL:
            time.sleep(0.1)
            # pass
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
        # self.dque = Queue()
        self.discr = 0

    def connect(self):
        return self.tcp_client.connect()

    def register(self):
        self.tcp_client.register_client()

    def disconnect(self):
        self.tcp_client.disconnect()

    def read_frame(self):
        try:
            result = self._read_frame()
        except struct.error:
            raise errors.TCPErrorBrokenPackage()
        else:
            return result

    def _read_frame(self):
        """ read frame according some weird frame format """
        while True:
            raw_data = self.tcp_client.get_next()
            if len(raw_data) >= 4:
                if self.formatter.decode_str('i', raw_data[:4]) == self.FRAME_TYPE:
                    break

        time_begin = self.formatter.decode_str(self.TIME_MASK, raw_data[4:20])
        time_end = self.formatter.decode_str(self.TIME_MASK, raw_data[20:36])
        # reserved = raw_data[36:64]
        discret_friq = self.formatter.decode_str('i', raw_data[64:68])
        # discret_friq = self.formatter.decode_str('f', raw_data[36:40])
        message = raw_data[68:]
        msg_len_needed = self.ARRAYS_NUMBER*self.ARRAY_ELEMENTS*2

        if len(message) < msg_len_needed:
            raise errors.TCPErrorBrokenPackage()

        raw_array = self.formatter.decode_str(self.ARRAY_MASK, message)

        arrays = list(self._chunks(raw_array, self.ARRAY_ELEMENTS))
        transponated = zip(*arrays)
        # print("reserved...")
        # for x in xrange(len(reserved)/2):
        #     # zug = reserved[4*x:4+4*x]
        #     zug = reserved[2*x:2+2*x]
        #     print(self.formatter.decode_str('h', zug))
        # print("\nbegin:\t{}\nend:\t{}\ndiscr:\t{}".format(
        #     time_begin, time_end, discret_friq
        #     ))
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
        while True:
            try:
                data, begin, end, discr = self.read_frame()
            except errors.TCPErrorBrokenPackage:
                pass
            except errors.TCPErrorServerDisconnect:
                data = [None]
                discr = None
                break
            else:
                break

        if self.discr != discr:
            self.discr = discr

        for line in data:
            self.que.put(line)

    def get_discr(self):
        return self.discr


class AsyncManager(object):
    """
    Manages Asyncronous tcp client

    public classes:
    - connect - connect to remote server
    - get - receive data pacakge with length equall frame size
    - disconnect - disconnect from remote server
    """
    OWERFLOW_RATE = 100
    # DEFAULT_DISCR = 1000

    def __init__(self, host, port, window=10, owerflow_rate=OWERFLOW_RATE):
        self.window = window
        self.owerflow_limit = window * owerflow_rate
        self.command_que = mp.Queue()
        self.data_que = mp.Queue()
        self.discr_que = mp.Queue()
        self.tcp_client = AsyncSocketListener(
            self.command_que, self.data_que, self.discr_que,
            (host, port)
            )
        self.discr = 0
        # self.discr = self.DEFAULT_DISCR

    def connect(self):
        self.tcp_client.start()
        self.command_que.put(COMMAND_CONNECT)
        self.command_que.put(COMMAND_REGISTER)
        # FIXIT: need to handle connection status
        return True

    def disconnect(self):
        self.command_que.put(COMMAND_DISCONNECT)
        time.sleep(0.01)
        self.tcp_client.terminate()
        # self.tcp_client.join()

    def get(self):
        step = self.data_que.qsize()/self.owerflow_limit
        data = self._get(self.window, step)
        discr = self._get_actual_discr(step)
        return data, discr

    def _get(self, number, step):
        """ receive <number> lines from tcp connection"""
        steppy = 0
        result = list()

        for x in xrange(number):
            while steppy < step:
                dummy = self.data_que.get()
                if not dummy:
                    return None
                steppy += 1
            else:
                next_line = self.data_que.get()
                if not next_line:
                    return None
                result.append(next_line)
                steppy = 0
        else:
            return result

    def _get_discr(self):
        try:
            discr = self.discr_que.get_nowait()
        except QueueEmpty:
            return self.discr
        else:
            if discr:
                self.discr = discr
            return self.discr

    def _get_actual_discr(self, step):
        discr = self._get_discr()
        actual = discr/(step+1)
        return actual

    # def _fill_discr(self):
    #     discr = self._get_discr()
    #     if discr:
    #         self.discr = discr


class AsyncSocketListener(mp.Process):
    """Asyncronous Socket Listener"""

    def __init__(self, command_que, data_que, discr_que, socket):
        mp.Process.__init__(self)
        self.command_que = command_que
        self.data_que = data_que
        self.discr_que = discr_que
        self.socket = socket
        self.next = False
        self.discr = None

    def run(self):
        """ main command listening loop """
        self.tcp_client = SpearmanSocketListener(*self.socket)

        while True:
            try:
                command = self.command_que.get_nowait()
            except QueueEmpty:
                if self.next:
                    self._default()
            else:
                result = self._command(command)
                if not result:
                    break

    def _command(self, command):
        """ handle outer command """
        if command == COMMAND_CONNECT:
            return self._connect()
        elif command == COMMAND_REGISTER:
            return self._register()
        elif command == COMMAND_DISCONNECT:
            return self._disconnect()

    def _connect(self):
        result = self.tcp_client.connect()
        if result:
            self.next = True
        return result

    def _register(self):
        self.tcp_client.register()
        return True

    def _disconnect(self):
        self.tcp_client.disconnect()
        self.next = False
        return False

    def _default(self):
        """
        receive next data line
        and put it into data queue
        """
        result = self.tcp_client.get()
        self.data_que.put(result)

    def _put_discr(self):
        discr = self.tcp_client.get_discr()
        if discr != self.discr:
            self.discr = discr
            self.discr_que.put(self.discr)


def main():
    tcp_client = AsyncManager("192.168.0.105", 8000)
    tcp_client.connect()
    data = tcp_client.get()
    for line in data:
        print(line)
    tcp_client.disconnect()
    print('ok')


if __name__ == '__main__':
    main()
