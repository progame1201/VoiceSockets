from .Netobject import NetObject


class Auth(NetObject):
    def __init__(self, password):
        super().__init__()
        self.password = password