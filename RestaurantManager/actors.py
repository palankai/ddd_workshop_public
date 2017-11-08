import time
from pprint import pprint

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

    def handle(self, order):
        time.sleep(.3)
        order.ingredients = []
        order.ingredients.append(
            {'name': 'cheese', 'qty': 3},
        )
        order.ingredients.append(
            {'name': 'mustard', 'qty': 5},
        )
        order.cook_time = 600
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


def main():
    printer = OrderPrinter()
    cashier = Cashier(printer)
    assman = AssistantManager(cashier)
    cook = Cook(assman)
    waiter = Waiter(cook)

    for indx in range(100):
        waiter.place_order(
            reference=f'ABC-{indx}',
            lines=[{'name': 'Cheese Pizza', 'qty': 1}]
        )
        cashier.pay(f'ABC-{indx}')


if __name__ == '__main__':
    main()
