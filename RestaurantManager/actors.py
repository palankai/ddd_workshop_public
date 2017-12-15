"""
Actors are the first class citizens of the application.

- Universal primitive of concurrent computation
- completely isolated from eachother

They can:
  - Send messages (to other actors)
  - create more actors
  - designate what to do with the next message

In our implementation they don't know anything about
the others.

The **Originator** doesn't receive any _Event_,
but it generate _Events_.

The **Enrichers** receive _Command_, do they part,
and they can send _Events_ as well.
"""
from pprint import pprint
import uuid
import time


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
    """
    Originator
    """

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
    """
    Enricher

    In this code it also responsible for deduplication,
    although it could be moved out to a reactor.
    """

    def __init__(self, bus, cooked, time_to_sleep, name):
        self._name = name
        self._time_to_sleep = time_to_sleep
        self._bus = bus
        self._cooked = cooked

    def handle(self, event):
        order = event.order
        if order.reference in self._cooked:
            print('*** DUPLICATED, IGNORE ***')
            return
        self._cooked.append(order.reference)
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
