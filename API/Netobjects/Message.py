from .Netobject import NetObject


class Message(NetObject):
    def __init__(self, data, send_from_id=None):
        super().__init__()
        self.data = data
        self.send_from = send_from_id