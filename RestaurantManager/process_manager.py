import functools

from messages import OrderPlaced, CookFood
from messages import FoodCooked, PriceOrder
from messages import OrderPriced, TakePayment
from messages import OrderPaid
from messages import OrderCompleted
from messages import DelayPublish, CookTimedOut


def methoddispatch(func):
    dispatcher = functools.singledispatch(func)
    def wrapper(*args, **kw):
        return dispatcher.dispatch(args[1].__class__)(*args, **kw)
    wrapper.register = dispatcher.register
    functools.update_wrapper(wrapper, func)
    return wrapper


class MidgetHouse:
    """
    The Main Process Manager which fires up the individual process managers
    I guess it's an Actor!
    """

    def __init__(self, bus):
        self._bus = bus
        # Keeps record of sub process managers
        self._midgets = {}

    def handle(self, message):
        # Message in this case is the start signal
        # It creates the rest of the flow
        # The flow itself related to the CorrelationId
        midget = MidgetForRegular(self._bus)
        self._midgets[message.correlation_id] = midget

        # It subscribe itself to *Every*
        # messages which sent with the correlation_id
        # of the message
        self._bus.subscribe(message.correlation_id, self.handle_by_correlation_id)

        # It basically ties the flow to the correlation id

    def handle_by_correlation_id(self, message):
        # Based on the correlation_id it is able to delegate the
        # message processing to the SubProcessManager
        if message.correlation_id in self._midgets:
            midget = self._midgets[message.correlation_id]
            midget.handle(message)

    def handle_unsubscribe(self, message):
        # When the stop signal received it tears down
        # the sub process managers
        if message.correlation_id in self._midgets:
            del self._midgets[message.correlation_id]
            self._bus.unsubscribe(message.correlation_id, self.handle_by_correlation_id)

    def get_info(self):
        return f'MidgetHouse: {len(self._midgets)}'

    def count(self):
        return len(self._midgets)


class MidgetForRegular:

    def __init__(self, bus):
        self._bus = bus
        self.handle = functools.singledispatch(self.handle)
        self.handle.register(OrderPlaced, self.handle_order_placed)
        self.handle.register(FoodCooked, self.handle_food_cooked)
        self.handle.register(OrderPriced, self.handle_order_priced)
        self.handle.register(OrderPaid, self.handle_order_paid)
        self.handle.register(CookTimedOut, self.handle_cook_timedout)
        self._cooked = []

    def handle(self, message):
        # Ignore messages that we don't want to process
        return

    def handle_order_placed(self, message):
        # Deduplication
        if message.order.reference in self._cooked:
            # If the food cooked we don't have to do
            # anything
            return
        # Create the Command for the next step in the
        # flow
        cmd = CookFood(
            message.order,
            correlation_id=message.correlation_id,
            causation_id=message.message_id
        )
        # Create an event, in this case the
        # of lost messages
        timeout = CookTimedOut(
            message.order,
            correlation_id=message.correlation_id,
            causation_id=message.message_id
        )

        # We send the timeout event in the future
        # and at the time we can check whether the
        # event has been processed as we expected
        self._bus.publish(
            'delay_publish',
            DelayPublish(
                delay=10,
                topic='timed_out',
                message=timeout,
                correlation_id=message.correlation_id,
                causation_id=message.message_id
            )
        )
        # We send the command to do the action
        self._bus.publish(
            'cook_food',
            cmd
        )

    def handle_cook_timedout(self, message):
        # In case of timeout we just do the action again
        self.handle_order_placed(message)
        return

    def handle_food_cooked(self, message):
        # For deduplication it manages it's own state
        # and stores the cooked food references
        self._cooked.append(message.order.reference)
        self._bus.publish(
            'price_order',
            PriceOrder(
                message.order,
                correlation_id=message.correlation_id,
                causation_id=message.message_id
            )
        )

    def handle_order_priced(self, message):
        self._bus.publish(
            'take_payment',
            TakePayment(
                message.order,
                correlation_id=message.correlation_id,
                causation_id=message.message_id
            )
        )

    def handle_order_paid(self, message):
        # This is a technical but important step.
        # In this flow, once the order paid the
        # order considered being completed.
        # In this case we send the `order_completed`
        # event which is the stop signal of the process manager
        self._bus.publish(
            'order_completed',
            OrderCompleted(
                message.order,
                correlation_id=message.correlation_id,
                causation_id=message.message_id
            )
        )



class MidgetForDoggy:

    def __init__(self, bus):
        self._bus = bus
        self.handle = functools.singledispatch(self.handle)
        self.handle.register(OrderPlaced, self.handle_order_placed)
        self.handle.register(OrderPriced, self.handle_order_priced)
        self.handle.register(OrderPaid, self.handle_order_paid)
        self.handle.register(FoodCooked, self.handle_food_cooked)

    def handle(self, message):
        # Ignore messages that we don't want to process
        return

    def handle_order_placed(self, message):
        self._bus.publish(
            'price_order',
            PriceOrder(
                message.order,
                correlation_id=message.correlation_id,
                causation_id=message.message_id
            )
        )

    def handle_order_priced(self, message):
        self._bus.publish(
            'take_payment',
            TakePayment(
                message.order,
                correlation_id=message.correlation_id,
                causation_id=message.message_id
            )
        )

    def handle_order_paid(self, message):
        self._bus.publish(
            'cook_food',
            CookFood(
                message.order,
                correlation_id=message.correlation_id,
                causation_id=message.message_id
            )
        )

    def handle_food_cooked(self, message):
        self._bus.publish(
            'order_completed',
            OrderCompleted(
                message.order,
                correlation_id=message.correlation_id,
                causation_id=message.message_id
            )
        )

