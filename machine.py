import messages


class Machine:

    def __init__(self, bus):
        self.bus = bus
        self.tensec = []
        self.fifteensec = []
        self.threshold = 0

    def process(self):
        message = self.bus.pop()
        if isinstance(message, messages.PositionAccured):
            self.set_price(message)
        elif isinstance(message, messages.PriceUpdated):
            self.handle_price_updated(message)
        elif isinstance(message, messages.RemoveFrom10Seconds):
            self.handle_remove_from_ten(message)
        elif isinstance(message, messages.RemoveFrom15Seconds):
            self.handle_remove_from_fifteen(message)
        elif isinstance(message, messages.GetOffPosition):
            self.sell()
        elif isinstance(message, messages.ThresholdUpdate):
            self.update_threshold(message)

    def handle_remove_from_ten(self, message):
        if len(self.tensec) > 1:
            self.tensec.pop(message.price)
        elif message.price < self.threshold:
            self.bus.publish(messages.GetOffPosition())

    def handle_remove_from_fifteen(self, message):
        if len(self.fifteensec) > 1:
            self.fifteensec.pop(message.price)
        elif message.price > self.threshold:
            self.bus.publish(messages.ThresholdUpdate(message.price))

    def handle_price_updated(self, message):
        self.bus.publish(messages.RemoveFrom10Seconds(message.price))
        self.bus.publish(messages.RemoveFrom15Seconds(message.price))

    def update_threshold(self, message):
        self.threshold = message.price

    def sell(self):
        self.bus.publish(messages.GetOffPosition())

    def set_price(self, message):
        self.tensec.append(message.price)
        self.fifteensec.append(message.price)
        self.threshold = int(message.price * 0.9)
