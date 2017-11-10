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

    def __init__(self, bus):
        self._bus = bus
        self._midgets = {}

    def handle(self, message):
        midget = MidgetForRegular(self._bus)
        self._midgets[message.correlation_id] = midget
        self._bus.subscribe(message.correlation_id, self.handle_by_correlation_id)

    def handle_by_correlation_id(self, message):
        if message.correlation_id in self._midgets:
            midget = self._midgets[message.correlation_id]
            midget.handle(message)

    def handle_unsubscribe(self, message):
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
        if message.order.reference in self._cooked:
            return
        cmd = CookFood(
            message.order,
            correlation_id=message.correlation_id,
            causation_id=message.message_id
        )
        timeout = CookTimedOut(
            message.order,
            correlation_id=message.correlation_id,
            causation_id=message.message_id
        )

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
        self._bus.publish(
            'cook_food',
            cmd
        )

    def handle_cook_timedout(self, message):
        if message.order.reference in self._cooked:
            return
        cmd = CookFood(
            message.order,
            correlation_id=message.correlation_id,
            causation_id=message.message_id
        )
        timeout = CookTimedOut(
            message.order,
            correlation_id=message.correlation_id,
            causation_id=message.message_id
        )

        self._bus.publish(
            'delay_publish',
            DelayPublish(
                delay=10,
                topic='cook_food',
                message=timeout,
                correlation_id=message.correlation_id,
                causation_id=message.message_id
            )
        )
        self._bus.publish(
            'cook_food',
            cmd
        )

    def handle_food_cooked(self, message):
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

