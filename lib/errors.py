class BaseError(Exception):
    """docstring for BaseError"""
    ERRORMSG = "Unexpected error"

    def __init__(self, text=ERRORMSG):
        self.text = text

    def __str__(self):
        return repr(self.text)


class TCPError(BaseError):
    pass


class TCPErrorBrokenPackage(TCPError):
    ERRORMSG = "Package is broken"


class TCPErrorServerDisconnect(TCPError):
    ERRORMSG = "Client was disconnected by server"
