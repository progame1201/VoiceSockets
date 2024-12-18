from .Netobject import NetObject


class Channels(NetObject):
    def __init__(self, channels):
        super().__init__()
        self.channels = channels