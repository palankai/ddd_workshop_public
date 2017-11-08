import typing


class Message(typing.NamedTuple):
    pass


class PositionAccured(Message):
    price: int


class PriceUpdated(Message):
    price: str


class SendToMeIn(Message):
    message: Message
    seconds: int


class RemoveFrom10Seconds(Message):
    price: int


class RemoveFrom15Seconds(Message):
    price: int
