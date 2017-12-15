"""
Every message should have tree very important identifier
A Message can be: Command or Event

MessageId:
  Unique id, identifies every single message
CausationId:
  Identifies the message which caused the message
  to be created
CorrelationId:
  Unique id, identifies the message flow.
  The first message in the flow (which doesn't have causation id)
  creates the CorrelationId. Every subsequent message should
  use the same CorrelationId.
"""
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


class DelayPublish(Command, Message):

    def __init__(self, delay, topic, message, correlation_id, causation_id=None, message_id=None):
        self.delay = delay
        self.message = message
        self.topic = topic
        super().__init__(correlation_id, causation_id, message_id)


class CookTimedOut(Event, OrderBased):
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
