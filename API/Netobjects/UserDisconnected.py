from .Netobject import NetObject


class UserDisconnected(NetObject):
    def __init__(self, id):
        super().__init__()
        self.id = id