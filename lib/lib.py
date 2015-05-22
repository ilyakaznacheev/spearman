import argparse
import httplib
from tcp_client import SpearmanSocketListener


INNER_SOCKET = ("127.0.0.1", 8000)

errors = {
    1: "\nGeneration concluded by user\n",
    2: "\nError while open {}\n"
}

json_example = {
    "keys": 5,
    "kfs": [
        [(1, 2), 0.45631546],
        [(1, 3), 0.4856231],
        [(1, 4), 0.89564156],
        [(1, 5), 0.3468456145],
        [(2, 3), 0.789564856],
        [(2, 4), 0.49651456],
        [(2, 5), 0.78456],
        [(3, 4), 0.9864512],
        [(3, 5), 0.325461523],
        [(4, 5), 0.84561532]
    ]
}


class ArgParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(ArgParser, self).__init__(*args, **kwargs)
        # self._initiate_params()

    def _initiate_params_file_gen(self):
        """initiate default parameters"""
        self.add_argument(
            "-f", "--file-name",
            dest="filename", required=True,
            help="path to output file"
            )
        self.add_argument(
            "-n", "--number-of-values",
            dest="number", type=int, default=3,
            help="number of values in line"
            )
        self.add_argument(
            "-s", "--sleep-time",
            dest="sleep", type=float, default=0.,
            help="time to idle between iterations"
            )

    def _initiate_params_reader(self):
        """initiate default parameters"""
        self.add_argument(
            "-f", "--file-name",
            dest="filename", required=True,
            help="path to output file"
            )
        self.add_argument(
            "-n", "--number-of-values",
            dest="number", type=int, default=3,
            help="number of values in line"
            )


class DataReader(object):
    """docstring for DataReader"""
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_line(self):
        pass


class NetReader(DataReader):
    """ Simple Socket client """
    def start(self, entry_port, entry_host):
        self.listener = SpearmanSocketListener(entry_host, int(entry_port))
        status = self.listener.connect()
        if status:
            self.listener.register()

        return status

    def get_line(self):
        line = self.listener.get()
        # print("line: {}".format(line))
        print('*'),
        return line

    def stop(self):
        self.listener.disconnect()


class FileReader(DataReader):
    """ Simple file reader """
    def start(self, entry_file):
        try:
            self.input_file = open(entry_file)
        except IOError:
            return False
        else:
            return True

    def get_line(self):
        raw_line = self.input_file.readline()
        return raw_line.split()

    def stop(self):
        self.input_file.close()
