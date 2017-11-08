class Bus:

    def publish(self, message):
        raise NotImplementedError()


class FakeBus:

    def __init__(self):
        self.clear()

    def publish(self, message):
        self._messages.append(message)

    def clear(self):
        self._messages = []
