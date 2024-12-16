from .Netobject import NetObject


class Auth(NetObject):
    def __init__(self, password, nickname):
        super().__init__()
        self.password = password
        self.nickname = nickname