import messages
from bus import FakeBus

from machine import Machine

class TestX:

    def _test_we_send_future_message_ourself(self):
        starter = messages.PositionAccured(100)
        bus = FakeBus()

        bus.publish(starter)

        first_message = bus.messages

        assert first_message == messages.SendToMeIn(messages.RemoveFrom10Seconds(100), 10)

    def test_price_goes_down(self):
        bus = FakeBus()
        thing = Machine(bus)

        bus.publish(messages.PositionAccured(100))
        thing.process()

        bus.publish(messages.PriceUpdated(99))
        thing.process()
        last_message = bus.messages.pop()
        assert isinstance(last_message, messages.RemoveFrom10Seconds)

    def _test_price_goes_up(self):
        bus = FakeBus()
        thing = Machine(bus)

        bus.publish(messages.PositionAccured(100))
        thing.process()
        bus.publish(messages.PriceUpdated(101))
        thing.process()

        last_message = bus.messages[-1]
        assert isinstance(last_message, messages.GetOffPosition)
