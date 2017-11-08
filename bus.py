class Bus:

    def publish(message):
        raise NotImplementedError()


class FakeBus:

    def __init__(self):
        self.clear()

    def publish(message):
        self._messages.append(message)

    def clear(self):
        self._messages = []
