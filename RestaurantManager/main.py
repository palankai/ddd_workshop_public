import os
import sys
import time

from buses import TopicBasedPubSub
from messages import OrderPlaced, OrderPriced, OrderPaid, FoodCooked
from actors import OrderPrinter, Cashier, Cook, Waiter, AssistantManager
from actors import QueueHandler, MoreFairDispatcher
from actors import Chaos
from actors import Monitor, AlarmClock
from process_manager import MidgetHouse


def main(envs, prog, raw_args):
    bus = TopicBasedPubSub()

    printer = OrderPrinter()

    cashier = Cashier(bus)

    assman = AssistantManager(bus)
    assman_queue = QueueHandler(assman, 'assmanQ')


    cook1 = Cook(bus, .1, 'Cook 1')
    cook2 = Cook(bus, .3, 'Cook 2')
    cook3 = Cook(bus, .5, 'Cook 3')
    queue_handler1 = QueueHandler(cook1, 'cook1Q')
    queue_handler2 = QueueHandler(cook2, 'cook2Q')
    queue_handler3 = QueueHandler(cook3, 'cook3Q')
    # multiplexer = RoundRobinDispatcher([queue_handler1, queue_handler2, queue_handler3])
    more_fair_dispatcher = MoreFairDispatcher([queue_handler1, queue_handler2, queue_handler3], 5)
    mfd_queue = QueueHandler(more_fair_dispatcher, 'MFD')
    cook_queue_chaos = Chaos(mfd_queue, 0.5, 0)

    waiter = Waiter(bus)
    alarm_clock = AlarmClock(bus)

    midget_house = MidgetHouse(bus)

    monitor = Monitor([
        queue_handler1, queue_handler2, queue_handler3, assman_queue,
        mfd_queue, cashier, midget_house, bus
    ])


    # Subscriptions
    # bus.subscribe('order_placed', mfd_queue.handle)
    # bus.subscribe('order_cooked', assman_queue.handle)
    # bus.subscribe('order_priced', cashier.handle)
    # bus.subscribe('order_paid', printer.handle)

    bus.subscribe('cook_food', cook_queue_chaos.handle)
    bus.subscribe('price_order', assman_queue.handle)
    bus.subscribe('take_payment', cashier.handle)

    bus.subscribe('order_paid', printer.handle)

    bus.subscribe('order_placed', midget_house.handle)
    bus.subscribe('order_completed', midget_house.handle_unsubscribe)

    bus.subscribe('delay_publish', alarm_clock.handle)

    # Start
    # bus.start()
    monitor.start()
    queue_handler1.start()
    queue_handler2.start()
    queue_handler3.start()
    assman_queue.start()
    mfd_queue.start()
    alarm_clock.start()



    for indx in range(100):
        event = waiter.place_order(
            doggy=False, # (indx % 2 == 0),
            paid=False,
            cooked=False,
            reference=f'ABC-{indx}',
            lines=[{'name': 'Cheese Pizza', 'qty': 1}]
        )
        bus.subscribe(event.correlation_id, printer.handle)


    paid_total = 0
    while paid_total < 101 and midget_house.count() > 0:
        for order in cashier.get_outstanding_orders():
            cashier.pay(order.reference)
            paid_total += 1
        print('Wait for more orders to come...')
        time.sleep(1)

    queue_handler1.stop()
    queue_handler2.stop()
    queue_handler3.stop()
    assman_queue.stop()
    mfd_queue.stop()
    monitor.stop()
    alarm_clock.stop()


if __name__ == '__main__':
    main(os.environ, sys.argv[0], sys.argv[1:])
