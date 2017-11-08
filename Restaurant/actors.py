from order import Order


class Waiter:

    def __init__(self, handler):
        self.handler = handler

    def handle(self):
        order = Order()
        return self.handler.handle(order)


class Cook:

    def __init__(self, handler):
        self.handler = handler

    def handle(self, order):
        order.add_line({'item': 'Cheese', 'qty': 1})
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
        return order.document
