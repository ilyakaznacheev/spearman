from tcp_client import SpearmanSocketListener, AsyncManager


class DataReader(object):
    """docstring for DataReader"""
    DEFAULT_DISCR = 1000

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_line(self):
        pass


class NetReader(DataReader):
    """ Simple Socket client """
    def start(self, entry_port, entry_host, entry_frame):
        self.listener = SpearmanSocketListener(entry_host, int(entry_port))
        status = self.listener.connect()
        if status:
            self.listener.register()

        return status

    def get_line(self):
        line = self.listener.get()
        print('*'),
        return line

    def get(self):
        pass

    def stop(self):
        self.listener.disconnect()


class AsyncReader(DataReader):
    """ Asynchronous Socket client """
    def start(self, entry_port, entry_host, entry_frame):
        self.listener = AsyncManager(
            entry_host, int(entry_port), int(entry_frame)
            )
        status = self.listener.connect()
        return status

    def get(self):
        lines, discr = self.listener.get()
        print('*'),
        if not discr:
            discr = self.DEFAULT_DISCR
        return lines, discr

    def stop(self):
        self.listener.disconnect()


class FileReader(DataReader):
    """ Simple file reader """
    def start(self, entry_file, entry_frame):
        self.window = int(entry_frame)
        try:
            self.input_file = open(entry_file)
        except IOError:
            return False
        else:
            return True

    def get_line(self):
        raw_line = self.input_file.readline()
        return raw_line.split()

    def get(self):
        result = list()
        for x in xrange(self.window):
            try:
                raw_line = self.input_file.readline()
            except ValueError:
                result = None
                break
            if not raw_line:
                result = None
                break

            result.append(raw_line.split())
        return result, self.DEFAULT_DISCR

    def stop(self):
        self.input_file.close()
