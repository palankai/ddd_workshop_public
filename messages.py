import typing


class PositionAccured(typing.NamedTuple):
    price: int


class PriceUpdated(typing.NamedTuple):
    price: str


class SendToMeIn(typing.NamedTuple):
    message: Message
    seconds: int


class RemoveFrom10Seconds(typing.NamedTuple):
    price: int


class RemoveFrom15Seconds(typing.NamedTuple):
    price: int
