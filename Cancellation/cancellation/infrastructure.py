class Bus:

    def __init__(self):
        self.messages = []

    def publish(self, messages):
        self.messages.extend(messages)
        messages.clear()


class Repository:

    def __init__(self, objects=None):
        self.objects = objects or dict()

    def add(self, obj):
        self.objects[obj.order_id] = obj

    def get(self, order_id):
        return self.objects[order_id]
