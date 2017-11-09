from json import loads as json_decode

import actors

# Haha!
actors.time.sleep = lambda a: None

class TestWaiter:

    def test_waiter_placing_order(self):
        waiter = actors.Waiter(actors.OrderPrinter())
        result = waiter.handle()

        assert json_decode(result) == {}

    def test_cook_and_waiter_placing_order(self):
        waiter = actors.Waiter(actors.Cook(actors.OrderPrinter()))
        result = waiter.handle()

        assert len(json_decode(result)['lines']) == 1
        assert json_decode(result)['lines'][0] == \
            {'id': 1, 'item': 'Cheese', 'qty': 1}

    def test_asst_man_cook_and_waiter_placing_order(self):
        cook = actors.Cook(actors.AsstMan(actors.OrderPrinter()))
        waiter = actors.Waiter(cook)
        result = waiter.handle()

        assert json_decode(result)['lines'][0]['price'] == 100

    def test_cashier_asst_man_cook_and_waiter_placing_order(self):
        cashier = actors.Cashier(actors.OrderPrinter())
        cook = actors.Cook(actors.AsstMan(cashier))
        waiter = actors.Waiter(cook)

        result = waiter.handle()

        assert json_decode(result)['paid'] is True
