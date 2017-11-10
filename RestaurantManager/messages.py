import json
import uuid

class Message:

    def __init__(self, correlation_id, causation_id=None, message_id=None):
        self.correlation_id = correlation_id
        self.causation_id = causation_id
        self.message_id = message_id or str(uuid.uuid4())


class OrderBased(Message):

    def __init__(self, order, correlation_id, causation_id=None, message_id=None):
        super().__init__(correlation_id, causation_id, message_id)
        self.order = order

    def serialize(self):
        return json.dumps({'order': self.order._src})

class Command(Message):
    pass

class Event(Message):
    pass


class CookFood(Command, OrderBased):
    pass


class PriceOrder(Command, OrderBased):
    pass


class TakePayment(Command, OrderBased):
    pass



class OrderPlaced(Event, OrderBased):
    pass


class FoodCooked(Event, OrderBased):
    pass


class OrderPriced(Event, OrderBased):
    pass


class OrderPaid(Event, OrderBased):
    pass

class OrderCompleted(Event, OrderBased):
    pass
