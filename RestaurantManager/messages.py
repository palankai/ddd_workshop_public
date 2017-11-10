import json

class Message:
    pass

class Command(Message):
    pass

class Event(Message):
    pass


class OrderBasedMixin:

    def __init__(self, order):
        self.order = order

    def serialize(self):
        return json.dumps({'order': self.order._src})


class CookFood(Command, OrderBasedMixin):
    pass


class PriceOrder(Command, OrderBasedMixin):
    pass


class TakePayment(Command, OrderBasedMixin):
    pass



class OrderPlaced(Event, OrderBasedMixin):
    pass


class FoodCooked(Event, OrderBasedMixin):
    pass


class OrderPriced(Event, OrderBasedMixin):
    pass


class OrderPaid(Event, OrderBasedMixin):
    pass
