import messages

class Machine:

    def __init__(self, bus):
        self.bus = bus
        self.min = 0
        self.max = 0

    def process(self):
        message = self.bus.get()
        if isinstance(message, messages.PositionAccured):
            self.set_price(message)
        elif isinstance(message, messages.PriceUpdated):
            self.handle_price_updated(message)

    def handle_price_updated(self, message):
        if message.price < self.min:
            self.bus.publish(messages.RemoveFrom10Seconds(message.price))

    def set_price(self, message):
        self.min = self.max = message.price
