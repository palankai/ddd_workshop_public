from pprint import pprint
import os
import queue
import threading
import time

from documents import OrderDocument


class HandleOrder:

    def handle(self, order):
        raise NotImplementedError()

class Forwarder:

    def __init__(self, handler):
        self._handler = handler

    def forward(self, order):
        self._handler.handle(order.copy())


class OrderPrinter(HandleOrder):

    def __init__(self):
        pass

    def handle(self, order):
        pprint(order)


class Waiter(Forwarder):
    """Originator"""

    def place_order(self, **kwargs):
        order = OrderDocument(kwargs)
        self.forward(order)


class Cook(HandleOrder, Forwarder):
    """Enricher"""

    def __init__(self, handler, time_to_sleep, name):
        self._name = name
        self._time_to_sleep = time_to_sleep
        super().__init__(handler)

    def handle(self, order):
        time.sleep(self._time_to_sleep)
        order.ingredients = []
        order.ingredients.append(
            {'name': 'cheese', 'qty': 3},
        )
        order.ingredients.append(
            {'name': 'mustard', 'qty': 5},
        )
        order.cook_time = 600
        order.made_it = self._name
        self.forward(order)


class AssistantManager(HandleOrder, Forwarder):
    """Enricher"""

    def handle(self, order):
        for l in order.lines:
            l.price = 12
        self.forward(order)


class Cashier(HandleOrder, Forwarder):
    """Enricher"""

    def __init__(self, handler):
        self._orders = {}
        super().__init__(handler)

    def handle(self, order):
        self._orders[order.reference] = order

    def pay(self, reference):
        order = self._orders[reference]
        order.paid = True
        self.forward(order)

    def get_outstanding_orders(self):
        orders = []
        for order in self._orders.values():
            if not hasattr(order, 'paid') or not order.paid:
                orders.append(order)
        return orders



class Multiplexer:

    def __init__(self, handlers):
        self._handlers = handlers

    def handle(self, order):
        for h in self._handlers:
            h.handle(order.copy())


class RoundRobinDispatcher:

    def __init__(self, handlers):
        self._handlers = list(handlers)

    def handle(self, order):
        handler = self._handlers.pop(0)
        self._handlers.append(handler)
        handler.handle(order.copy())


class QueueHandler:

    def __init__(self, handler, name):
        self._name = name
        self._handler = handler
        self._queue = queue.Queue()
        self._running = False

    def handle(self, order):
        self._queue.put(order.copy())

    def get_queue_size(self):
        return self._queue.qsize()

    def get_name(self):
        return self._name

    def start(self):
        assert not self._running
        self._running = True

        def internal():
            while self._running:
                if self._queue.empty():
                    time.sleep(.5)
                    continue
                order = self._queue.get(False)
                self._handler.handle(order)

        manager = threading.Thread(target=internal)
        manager.start()

    def stop(self):
        self._running = False

class Monitor:

    def __init__(self, handlers):
        self._handlers = handlers
        self._running = False

    def start(self):
        assert not self._running
        self._running = True
        def internal():
            while self._running:
                print('*' * 40)
                for handler in self._handlers:
                    print('*', handler.get_name(), handler.get_queue_size())
                print('*' * 40)
                time.sleep(.8)

        manager = threading.Thread(target=internal)
        manager.start()

    def stop(self):
        self._running = False

def main():
    printer = OrderPrinter()
    cashier = Cashier(printer)
    assman = AssistantManager(cashier)
    assman_queue = QueueHandler(assman, 'assmanQ')
    cook1 = Cook(assman_queue, .1, 'Cook 1')
    cook2 = Cook(assman_queue, .3, 'Cook 2')
    cook3 = Cook(assman_queue, .5, 'Cook 3')
    queue_handler1 = QueueHandler(cook1, 'cook1Q')
    queue_handler2 = QueueHandler(cook2, 'cook2Q')
    queue_handler3 = QueueHandler(cook3, 'cook3Q')
    multiplexer = RoundRobinDispatcher([queue_handler1, queue_handler2, queue_handler3])
    waiter = Waiter(multiplexer)

    for indx in range(100):
        waiter.place_order(
            reference=f'ABC-{indx}',
            lines=[{'name': 'Cheese Pizza', 'qty': 1}]
        )
    queue_handler1.start()
    queue_handler2.start()
    queue_handler3.start()
    assman_queue.start()
    monitor = Monitor([queue_handler1, queue_handler2, queue_handler3, assman_queue])
    monitor.start()


    paid_total = 0
    while paid_total < 100:
        for order in cashier.get_outstanding_orders():
            cashier.pay(order.reference)
            paid_total += 1
        print('Wait for more orders to come...')
        time.sleep(1)

    queue_handler1.stop()
    queue_handler2.stop()
    queue_handler3.stop()
    assman_queue.stop()
    monitor.stop()


if __name__ == '__main__':
    main()
