import actors


cashier = actors.Cashier(actors.OrderPrinter())
assman = actors.ThreadedHandler(actors.AsstMan(cashier))

cook_one = actors.ThreadedHandler(actors.Cook(assman, '1'))
cook_two = actors.ThreadedHandler(actors.Cook(assman, '2'))
cook_three = actors.ThreadedHandler(actors.Cook(assman, '3'))

waiter = actors.Waiter(
    actors.RoundRobinDispatcher([cook_one, cook_two, cook_three]),
)

assman.start()
cook_one.start()
cook_two.start()
cook_three.start()

for _ in range(100):
    waiter.handle()
