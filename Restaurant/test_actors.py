import actors


class TestWaiter:

    def test_waiter_placing_order(self):
        waiter = actors.Waiter(actors.OrderPrinter())
        waiter.place_order()

    def test_cook_and_waiter_placing_order(self):
        waiter = actors.Waiter(actors.Cook(actors.OrderPrinter()))
        waiter.place_order()
