import os
import sys
import time

from buses import TopicBasedPubSub
from messages import OrderPlaced, OrderPriced, OrderPaid, FoodCooked
from actors import OrderPrinter, Cashier, Cook, Waiter, AssistantManager
from reactors import QueueHandler, MoreFairDispatcher
from reactors import Chaos
from reactors import Monitor, AlarmClock
from process_manager import MidgetHouse


def main(envs, prog, raw_args):
    # The backbone of the application, the messaging system
    bus = TopicBasedPubSub()

    # Actors
    # They might have bus as an input or any other infrastructure
    # requirement, but they don't know each other, therefore the order
    # of instantiation doesn't matter.

    # Cook has a shared state, the cooked food (for deduplication)
    cooked = []
    cook1 = Cook(bus, cooked, .1, 'Cook 1')
    cook2 = Cook(bus, cooked, .3, 'Cook 2')
    cook3 = Cook(bus, cooked, .5, 'Cook 3')
    printer = OrderPrinter()
    waiter = Waiter(bus)
    cashier = Cashier(bus)
    assman = AssistantManager(bus)


    assman_queue = QueueHandler(assman, 'assmanQ')
    cook1_queue = QueueHandler(cook1, 'cook1Q')
    cook2_queue = QueueHandler(cook2, 'cook2Q')
    cook3_queue = QueueHandler(cook3, 'cook3Q')
    
    # multiplexer = RoundRobinDispatcher([cook1_queue, cook2_queue, cook3_queue])
    cooks_dispatcher = MoreFairDispatcher([cook1_queue, cook2_queue, cook3_queue], 5)
    cooks_dispatcher_queue = QueueHandler(cooks_dispatcher, 'MFD')
    cooks_chaos = Chaos(cooks_dispatcher_queue, 0.3, 0.3)

    alarm_clock = AlarmClock(bus)

    midget_house = MidgetHouse(bus)

    monitor = Monitor([
        cook1_queue, cook2_queue, cook3_queue,
        assman_queue, cashier,
        cooks_dispatcher_queue, midget_house, bus
    ])


    # Cook (eventually) responds to the `CookFood` Command
    bus.subscribe('cook_food', cooks_chaos.handle)

    # AssistantManager responds to the `PriceOrder` Command
    bus.subscribe('price_order', assman_queue.handle)

    # Cashier responds to the `TakePayment` Command
    bus.subscribe('take_payment', cashier.handle)

    # Printer prints the document
    bus.subscribe('order_paid', printer.handle)

    # The process manager responds to the `OrderPlaced` event
    # and the `OrderCompleted` event.
    # These are the *Start* and *End* signals of the process manager
    bus.subscribe('order_placed', midget_house.handle)
    bus.subscribe('order_completed', midget_house.handle_unsubscribe)

    # The alarm clock responds the `DelayPublished` command
    bus.subscribe('delay_publish', alarm_clock.handle)

    # Start
    # Start all of the services, fire up queues
    monitor.start()
    cook1_queue.start()
    cook2_queue.start()
    cook3_queue.start()
    cooks_dispatcher_queue.start()
    assman_queue.start()
    alarm_clock.start()

    # From this point forward the system is ready to process


    # Place 100 orders
    # based on the `doggy` flag, the Process manager can decide
    # which flow should be followed
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
        print(f'Wait for more orders to come...')
        time.sleep(1)

    cook1_queue.stop()
    cook2_queue.stop()
    cook3_queue.stop()
    assman_queue.stop()
    cooks_dispatcher_queue.stop()
    monitor.stop()
    alarm_clock.stop()


if __name__ == '__main__':
    main(os.environ, sys.argv[0], sys.argv[1:])
