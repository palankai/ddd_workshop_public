import asyncio

import actors


cashier = actors.Cashier(actors.OrderPrinter())

waiter = actors.Waiter(
    actors.RoundRobinDispatcher([
        actors.Cook(cashier, '1'),
        actors.Cook(cashier, '2'),
        actors.Cook(cashier, '3'),
    ])
)
for _ in range(10):
    waiter.handle()
