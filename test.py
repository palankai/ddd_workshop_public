from messages import PositionAccured, SendToMeIn, RemoveFrom10Seconds
from bus import FakeBus


class TestX:

    def test_we_send_future_message_ourself(self):
        starter = PositionAccured()
        bus = FakeBus()

        bus.publish(starter)

        first_message = bus.messages

        assert first_message == SendToMeIn(RemoveFrom10Seconds(100), 10)
