from pprint import pprint
import collections
import os
import queue
import threading
import time

from documents import OrderDocument
from buses import TopicBasedPubSub
from messages import OrderPlaced, OrderPriced, OrderPaid, FoodCooked
from conrurrency import ThreadProcessor


class OrderPrinter:

    def __init__(self):
        pass

    def handle(self, event):
        pprint(event.order)


class Waiter:
    """Originator"""

    def __init__(self, bus):
        self._bus = bus

    def place_order(self, **kwargs):
        order = OrderDocument(kwargs)
        self._bus.publish('order_placed', OrderPlaced(order))


class Cook:
    """Enricher"""

    def __init__(self, bus, time_to_sleep, name):
        self._name = name
        self._time_to_sleep = time_to_sleep
        self._bus = bus

    def handle(self, event):
        order = event.order
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
        self._bus.publish('order_cooked', FoodCooked(order))


class AssistantManager:
    """Enricher"""

    def __init__(self, bus):
        self._bus = bus

    def handle(self, event):
        order = event.order
        for l in order.lines:
            l.price = 12
        self._bus.publish('order_priced', OrderPriced(order))


class Cashier:
    """Enricher"""

    def __init__(self, bus):
        self._orders = {}
        self._processed = 0
        self._bus = bus

    def handle(self, event):
        order = event.order
        self._orders[order.reference] = order

    def pay(self, reference):
        order = self._orders[reference]
        order.paid = True
        self._processed += 1
        self._bus.publish('order_paid', OrderPriced(order))

    def get_info(self):
        return f'Processed: {self._processed}'

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


class MoreFairDispatcher:

    def __init__(self, handlers, limit):
        self._limit = limit
        self._handlers = handlers

    def handle(self, order):
        handler = None
        while handler is None:
            handler = self._pick_one_handler()
        handler.handle(order)

    def _pick_one_handler(self):
        for handler in self._handlers:
            if handler.get_queue_size() < self._limit:
                return handler


class QueueHandler(ThreadProcessor):

    def __init__(self, handler, name):
        self._name = name
        self._handler = handler
        self._queue = queue.Queue()
        super().__init__()

    def handle(self, order):
        self._queue.put(order)

    def get_queue_size(self):
        return self._queue.qsize()

    def get_name(self):
        return self._name

    def get_info(self):
        return f'{self.get_name()}: {self.get_queue_size()}'

    def run_once(self):
        try:
            order = self._queue.get(timeout=1)
        except queue.Empty:
            return
        self._handler.handle(order)





class Monitor(ThreadProcessor):

    def __init__(self, handlers):
        self._handlers = handlers
        super().__init__()

    def run_once(self):
        print('*' * 40)
        for handler in self._handlers:
            print('*', handler.get_info())
        print('*' * 40)
        time.sleep(.5)


def main():
    bus = TopicBasedPubSub()

    printer = OrderPrinter()

    cashier = Cashier(bus)

    assman = AssistantManager(bus)
    assman_queue = QueueHandler(assman, 'assmanQ')


    cook1 = Cook(bus, .1, 'Cook 1')
    cook2 = Cook(bus, .3, 'Cook 2')
    cook3 = Cook(bus, .5, 'Cook 3')
    queue_handler1 = QueueHandler(cook1, 'cook1Q')
    queue_handler2 = QueueHandler(cook2, 'cook2Q')
    queue_handler3 = QueueHandler(cook3, 'cook3Q')
    # multiplexer = RoundRobinDispatcher([queue_handler1, queue_handler2, queue_handler3])
    more_fair_dispatcher = MoreFairDispatcher([queue_handler1, queue_handler2, queue_handler3], 5)
    mfd_queue = QueueHandler(more_fair_dispatcher, 'MFD')

    waiter = Waiter(bus)

    monitor = Monitor([queue_handler1, queue_handler2, queue_handler3, assman_queue, mfd_queue, cashier])

    # Subscriptions
    bus.subscribe('order_placed', mfd_queue.handle)
    bus.subscribe('order_cooked', assman_queue.handle)
    bus.subscribe('order_priced', cashier.handle)
    bus.subscribe('order_paid', printer.handle)



    # Start
    # bus.start()
    monitor.start()
    queue_handler1.start()
    queue_handler2.start()
    queue_handler3.start()
    assman_queue.start()
    mfd_queue.start()



    for indx in range(100):
        waiter.place_order(
            reference=f'ABC-{indx}',
            lines=[{'name': 'Cheese Pizza', 'qty': 1}]
        )


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
    mfd_queue.stop()
    monitor.stop()


if __name__ == '__main__':
    main()
