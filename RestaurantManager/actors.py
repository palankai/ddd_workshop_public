from pprint import pprint
import collections
import os
import queue
import threading
import time
import uuid
import random
import datetime

from conrurrency import ThreadProcessor
from documents import OrderDocument
from messages import OrderPlaced, OrderPriced, OrderPaid, FoodCooked


def get_uuid():
    return str(uuid.uuid4())


class OrderPrinter:

    def __init__(self):
        pass

    def handle(self, event):
        return
        print(f'{type(event)}; MessageId: {event.message_id} Caused by: {event.causation_id}, Correlation: {event.correlation_id}\n{event.order}')


class Waiter:
    """Originator"""

    def __init__(self, bus):
        self._bus = bus

    def place_order(self, **kwargs):
        order = OrderDocument(kwargs)
        event = OrderPlaced(
            order=order,
            correlation_id=get_uuid(),
        )
        self._bus.publish('order_placed', event)
        return event



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
        order.cooked = True
        self._bus.publish(
            'order_cooked',
            FoodCooked(
                order,
                correlation_id=event.correlation_id,
                causation_id=event.message_id
            )
        )


class AssistantManager:
    """Enricher"""

    def __init__(self, bus):
        self._bus = bus

    def handle(self, event):
        order = event.order
        for l in order.lines:
            l.price = 12
        self._bus.publish(
            'order_priced',
            OrderPriced(
                order,
                correlation_id=event.correlation_id,
                causation_id=event.message_id
            )
        )


class Cashier:
    """Enricher"""

    def __init__(self, bus):
        self._orders = {}
        self._processed = 0
        self._bus = bus

    def handle(self, event):
        order = event.order
        self._orders[order.reference] = event

    def pay(self, reference):
        event = self._orders[reference]
        order = event.order
        order.paid = True
        self._processed += 1
        self._bus.publish(
            'order_paid',
            OrderPaid(
                order,
                correlation_id=event.correlation_id,
                causation_id=event.message_id
            )
        )

    def get_info(self):
        return f'Processed: {self._processed}'

    def get_outstanding_orders(self):
        orders = []
        for event in self._orders.values():
            order = event.order
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


class AlarmClock(ThreadProcessor):

    def __init__(self, bus):
        self._messages = []
        self._bus = bus
        super().__init__()

    def handle(self, message):
        when = datetime.datetime.utcnow() + datetime.timedelta(seconds=message.delay)
        self._messages.append((when, message))

    def run_once(self):
        now = datetime.datetime.utcnow()
        for element in list(self._messages):
            when, message = element
            if now > when:
                self._bus.publish(message.topic, message.message)
                self._messages.remove(element)
                print('******* WAKE **********')
        time.sleep(1)



class Chaos:

    def __init__(self, handler, loose_ratio=0.3, duplication_ratio=0.4):
        self._handler = handler
        self._loose_ratio = loose_ratio
        self._duplication_ratio = duplication_ratio
        random.seed()

    def handle(self, event):
        rnd = random.random()
        if rnd > (self._loose_ratio + self._duplication_ratio):
            self._handler.handle(event)
        elif rnd > self._loose_ratio:
            self._handler.handle(event)
            self._handler.handle(event)


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
