import threading
import time

import actors


cashier = actors.Cashier(actors.OrderPrinter())
assman = actors.ThreadedHandler(actors.AsstMan(cashier), name='Ass Man')

cook_one = actors.ThreadedHandler(actors.Cook(assman, 'One', 1), name='Cook One')
cook_two = actors.ThreadedHandler(actors.Cook(assman, 'Two', 3), name='Cook Two')
cook_three = actors.ThreadedHandler(actors.Cook(assman, 'Three', 5), name='Cook Three')

dispatcher = actors.ThreadedHandler(actors.MoreFairDispatcher([cook_one, cook_two, cook_three]))

waiter = actors.Waiter(dispatcher)

dispatcher.start()
assman.start()
cook_one.start()
cook_two.start()
cook_three.start()

monitor = actors.Monitor([assman, cook_one, cook_two, cook_three, dispatcher])
monitor.start()

for _ in range(100):
    waiter.handle()
