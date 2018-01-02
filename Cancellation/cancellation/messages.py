from typing import NamedTuple


class CancellationRequested(NamedTuple):
    order_id: int

class CancellationSkipped(NamedTuple):
    order_id: int

class CancellationAccepted(NamedTuple):
    order_id: int

class CancellationRejected(NamedTuple):
    order_id: int



class CancelAtWarehouse(NamedTuple):
    order_id: int

class CancelAtHacienda(NamedTuple):
    order_id: int

class CancelAtERP(NamedTuple):
    order_id: int
