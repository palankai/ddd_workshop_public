import time
from order import Order
import threading
import uuid


class Waiter:

    def __init__(self, handler):
        self.handler = handler

    def handle(self):
        order = Order()
        return self.handler.handle(order)


class Cook:

    def __init__(self, handler, name=None):
        self.handler = handler
        self.name = name

    def handle(self, order):
        order.add_line({'cook': self.name, 'item': 'Cheese', 'qty': 1})
        time.sleep(2)
        return self.handler.handle(order)


class AsstMan:

    def __init__(self, handler):
        self.handler = handler

    def handle(self, order):
        order.add_price(1, 100)
        return self.handler.handle(order)


class Cashier:

    def __init__(self, handler):
        self.handler = handler

    def handle(self, order):
        order.pay_all()
        return self.handler.handle(order)


class OrderPrinter:

    def handle(self, order):
        print(order.document)


class OrderString:

    def handle(self, order):
        return order.document


class Multiplexor:

    def __init__(self, handlers):
        self.handlers = handlers

    def handle(self, order):
        for handler in self.handlers:
            handler.handle(order)


class RoundRobinDispatcher:

    def __init__(self, handlers):
        self.handlers = handlers

    def handle(self, order):
        handler = self.handlers.pop(0)
        handler.handle(order)
        self.handlers.append(handler)


class ThreadedHandler:

    def __init__(self, handler, name=None):
        self.handler = handler
        self.queue = []
        self.name = name or str(uuid.uuid4())[:4]

    def handle(self, order):
        self.queue.append(order)

    def get_info(self):
        return '{}: {}'.format(self.name, len(self.queue))

    def start(self):
        def process():
            while True:
                if len(self.queue) > 0:
                    order = self.queue.pop(0)
                    self.handler.handle(order)
                else:
                    time.sleep(0.5)
        threading.Thread(target=process).start()


class Monitor:

    def __init__(self, handler):
        self.handlers = handler

    def start(self):
        def process():
            while True:
                time.sleep(5)
                for handler in self.handlers:
                    print(handler.get_info())
        threading.Thread(target=process).start()
