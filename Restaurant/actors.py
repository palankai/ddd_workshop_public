import time
import random
import queue
import threading
import uuid

from order import Order


MAX_QUEUED = 5


class Waiter:

    def __init__(self, handler):
        self.handler = handler

    def handle(self):
        order = Order()
        return self.handler.handle(Order(order.document))


class Cook:

    def __init__(self, handler, name=None, eficiency=None):
        self.handler = handler
        self.eficiency = eficiency or random.randint(1, 5)
        self.name = '{}: ({})'.format(name, 'x' * self.eficiency)

    def handle(self, order):
        order.add_line({'cook': self.name, 'item': 'Cheese', 'qty': 1})
        time.sleep(self.eficiency)
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


class MoreFairDispatcher:

    def __init__(self, handlers):
        self.handlers = handlers

    def handle(self, order):
        handler = self.handlers.pop(0)
        if handler.count < MAX_QUEUED:
            handler.handle(order)
        else:
            time.sleep(.2)
        self.handlers.append(handler)


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
        self.queue = queue.Queue()
        self.name = name or str(uuid.uuid4())[:4]

    @property
    def count(self):
        return self.queue.qsize()

    def handle(self, order):
        self.queue.put(order)

    def get_info(self):
        return '{}: {}'.format(self.name, self.count)

    def start(self):
        def process():
            while True:
                order = self.queue.get()
                if order is None:
                    time.sleep(0.5)
                else:
                    self.handler.handle(order)
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
