from .Netobject import NetObject


class UserConnected(NetObject):
    def __init__(self, id):
        super().__init__()
        self.id = id