from bus import FakeBus
from machine import Machine
import messages


class TestMachine:

    def test_price_goes_down(self):
        # Given
        bus = FakeBus()
        machine = Machine(bus)

        bus.publish(messages.PositionAccured(100))

        # Because
        bus.publish(messages.PriceUpdated(99))
        machine.process_everything()

        # We should have
        assert messages.RemoveFrom15Seconds(99) in bus.messages
        assert messages.RemoveFrom10Seconds(99) in bus.messages

    def test_price_goes_down_but_not_bellow_threshold(self):
        # Given
        bus = FakeBus()
        machine = Machine(bus)

        bus.publish(messages.PositionAccured(100))
        bus.publish(messages.PriceUpdated(99))
        machine.process_everything()
        bus.clear()

        # Because
        bus.publish(messages.RemoveFrom10Seconds(99))
        machine.process()

        # We should have
        assert len(bus.messages) == 0

    def test_price_goes_up(self):
        # Given
        bus = FakeBus()
        machine = Machine(bus)

        bus.publish(messages.PositionAccured(100))

        # Because
        bus.publish(messages.PriceUpdated(101))
        machine.process_everything()

        # We should
        assert messages.RemoveFrom15Seconds(101) in bus.messages
        assert messages.RemoveFrom10Seconds(101) in bus.messages

    def test_price_keeps_going_down(self):
        # Given
        bus = FakeBus()
        machine = Machine(bus)

        bus.publish(messages.PositionAccured(100))
        machine.process()
        bus.publish(messages.PriceUpdated(89))
        machine.process()

        bus.clear()

        # Because price keeps going down
        bus.publish(messages.RemoveFrom10Seconds(89))
        machine.process()

        # We should
        assert messages.GetOffPosition() in bus.messages

    def test_price_keeps_going_down_and_down(self):
        # Given
        bus = FakeBus()
        machine = Machine(bus)

        bus.publish(messages.PositionAccured(100))
        machine.process()
        bus.publish(messages.PriceUpdated(89))
        machine.process()

        bus.clear()

        # Because price keeps going down
        bus.publish(messages.RemoveFrom10Seconds(89))
        bus.publish(messages.RemoveFrom10Seconds(89))
        machine.process_everything()

        # We should
        assert messages.GetOffPosition() in bus.messages

    def test_price_keeps_going_up(self):
        # Give
        bus = FakeBus()
        machine = Machine(bus)

        bus.publish(messages.PositionAccured(100))
        bus.publish(messages.PriceUpdated(101))
        machine.process_everything()
        bus.clear()

        # Because price keeps going down
        bus.publish(messages.RemoveFrom15Seconds(101))
        machine.process()

        # We should update threshold
        assert messages.ThresholdUpdate(101) in bus.messages
