import typing


class PositionAccured(typing.NamedTuple):
    price: int
    threshold: int

class PriceUpdated(typing.NamedTuple):
    price: int

class RemoveFrom10Seconds(typing.NamedTuple):
    price: int

class RemoveFrom15Seconds(typing.NamedTuple):
    price: int

class GetOffPosition(typing.NamedTuple):
    pass

class ThresholdUpdated(typing.NamedTuple):
    threshold: int

class SendMeIn(typing.NamedTuple):
    message: typing.NamedTuple
    seconds: int


class Bus:

    def __init__(self):
        self.clear()

    def clear(self):
        self.messages = []

    def remove_first(self):
        if len(self.messages):
            self.messages.pop(0)

    def publish(self, message):
        self.messages.append(message)


class StateMachine:


    def __init__(self):
        self.mapping = {
            PositionAccured: self.handle_position_aqquired,
            PriceUpdated: self.handle_price_updated,
            RemoveFrom10Seconds: self.handle_remove_from_10_seconds,
            RemoveFrom15Seconds: self.handle_remove_from_15_seconds
        }
        self.prices = []
        self.thresholds = []
        self.th = None
        self.finished = False

    def process(self, bus):
        for message in bus.messages:
            if type(message) in self.mapping:
                handler = self.mapping[type(message)]
                handler(bus, message)

    def handle_position_aqquired(self, bus, message):
        self.th = message.threshold

    def handle_price_updated(self, bus, message):
        self.prices.append(message.price)
        self.thresholds.append(message.price)
        bus.publish(SendMeIn(RemoveFrom10Seconds(message.price), 10))
        bus.publish(SendMeIn(RemoveFrom15Seconds(message.price), 15))

    def handle_remove_from_10_seconds(self, bus, message):
        if max(self.prices) <= self.th:
            bus.publish(GetOffPosition())
        else:
            self.prices.remove(message.price)

    def handle_remove_from_15_seconds(self, bus, message):
        if self.th <= min(self.thresholds):
            self.th = min(self.thresholds)
            bus.publish(ThresholdUpdated(self.th))
        self.thresholds.remove(message.price)


class Test10Seconds:

    def test_price_updated(self):
        # Given
        bus = Bus()
        sm = StateMachine()

        bus.publish(PositionAccured(price=100, threshold=90))
        bus.clear()


        # When
        bus.publish(PriceUpdated(101))
        sm.process(bus)


        # Then
        expected1 = SendMeIn(RemoveFrom15Seconds(101), 15)
        expected2 = SendMeIn(RemoveFrom10Seconds(101), 10)

        assert bus.messages[-1] == expected1
        assert bus.messages[-2] == expected2

    def test_when_value_is_below_threshold_and_all(self):

        # Given
        bus = Bus()
        sm = StateMachine()

        bus.publish(PositionAccured(price=100, threshold=90))
        bus.publish(PriceUpdated(89))
        sm.process(bus)
        bus.clear()


        # When
        bus.publish(RemoveFrom10Seconds(89))
        sm.process(bus)


        # Then
        expected = GetOffPosition()
        assert bus.messages[-1] == expected

    def test_when_value_is_below_threshold_but_not_all(self):

        # Given
        bus = Bus()
        sm = StateMachine()

        bus.publish(PositionAccured(price=100, threshold=90))
        bus.publish(PriceUpdated(95))
        bus.publish(PriceUpdated(89))
        sm.process(bus)
        bus.clear()


        # When
        bus.publish(RemoveFrom10Seconds(89))
        sm.process(bus)
        bus.remove_first()


        # Then
        assert len(bus.messages) == 0

    def test_when_value_is_above_treshold(self):

        # Given
        bus = Bus()
        sm = StateMachine()

        bus.publish(PositionAccured(price=100, threshold=90))
        bus.publish(PriceUpdated(93))
        sm.process(bus)
        bus.clear()


        # When
        bus.publish(RemoveFrom10Seconds(93))
        sm.process(bus)
        bus.remove_first()


        # Then
        assert len(bus.messages) == 0


class Test15Seconds:

    def test_when_value_is_above_threshold_and_all(self):

        # Given
        bus = Bus()
        sm = StateMachine()

        bus.publish(PositionAccured(price=100, threshold=90))
        bus.publish(PriceUpdated(93))
        sm.process(bus)
        bus.clear()


        # When
        bus.publish(RemoveFrom15Seconds(93))
        sm.process(bus)

        # Then
        expected = ThresholdUpdated(93)
        assert isinstance(bus.messages[-1], ThresholdUpdated)
        assert bus.messages[-1] == expected

    def test_when_value_is_above_threshold_but_not_all(self):

        # Given
        bus = Bus()
        sm = StateMachine()

        bus.publish(PositionAccured(price=100, threshold=90))
        bus.publish(PriceUpdated(95))
        bus.publish(PriceUpdated(89))
        sm.process(bus)
        bus.clear()


        # When
        bus.publish(RemoveFrom15Seconds(95))
        sm.process(bus)
        bus.remove_first()


        # Then
        assert len(bus.messages) == 0

    def test_when_value_is_below_treshold(self):

        # Given
        bus = Bus()
        sm = StateMachine()

        bus.publish(PositionAccured(price=100, threshold=90))
        bus.publish(PriceUpdated(89))
        sm.process(bus)
        bus.clear()


        # When
        bus.publish(RemoveFrom15Seconds(89))
        sm.process(bus)
        bus.remove_first()


        # Then
        assert len(bus.messages) == 0
