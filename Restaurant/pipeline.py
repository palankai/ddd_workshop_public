import asyncio

import actors


cashier = actors.Cashier(actors.OrderPrinter())

waiter = actors.Waiter(
    actors.Multiplexor([
        actors.Cook(cashier, '1'),
        actors.Cook(cashier, '2'),
        actors.Cook(cashier, '3'),
    ])
)
waiter.handle()
