import actors


class TestWaiter:

    def test_placing_order(self):
        waiter = actors.Waiter(actors.OrderPrinter())
        waiter.place_order()
