import pickle


class NetObject:
    def __init__(self):
        pass

    def serialize(self):
        return pickle.dumps(self)

    @classmethod
    def deserialize(cls, data):
        return pickle.loads(data)