import functools

from messages import OrderPlaced, CookFood
from messages import FoodCooked, PriceOrder
from messages import OrderPriced, TakePayment


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
        midget = Midget(self._bus)
        self._midgets[message.correlation_id] = midget
        self._bus.subscribe(message.correlation_id, self.handle_by_correlation_id)

    def handle_by_correlation_id(self, message):
        midget = self._midgets[message.correlation_id]
        midget.handle(message)


class Midget:

    def __init__(self, bus):
        self._bus = bus
        self.handle = functools.singledispatch(self.handle)
        self.handle.register(OrderPlaced, self.handle_order_placed)
        self.handle.register(FoodCooked, self.handle_food_cooked)
        self.handle.register(OrderPriced, self.handle_order_priced)

    def handle(self, message):
        # Ignore messages that we don't want to process
        return

    def handle_order_placed(self, message):
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
