from order import Order


class Waiter:

    def __init__(self, handler):
        self.handler = handler

    def place_order(self):
        order = Order()
        self.handler.handle(order)


class OrderPrinter:

    def handle(self, order):
        print(order.document)
