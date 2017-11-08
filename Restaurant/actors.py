from order import Order


class Waiter:

    def __init__(self, handler):
        self.handler = handler

    def place_order(self):
        order = Order()
        self.handler.handle(order)

class Cook:

    def __init__(self, handler):
        self.handler = handler

    def handle(self, order):
        order.add_line({'item': 'Cheese', 'qty': 1, 'price': 1})
        self.handler.handle(order)


class OrderPrinter:

    def handle(self, order):
        print(order.document)
