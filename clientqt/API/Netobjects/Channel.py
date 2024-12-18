from .Netobject import NetObject


class Channel(NetObject):
    def __init__(self, channel):
        super().__init__()
        self.channel = channel