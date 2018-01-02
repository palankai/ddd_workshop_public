from .models import Cancellation


def handle_cancellation_requested(repository, bus, event):
    cancellation = Cancellation(event.order_id)
    cancellation.requested()

    repository.add(cancellation)
    bus.publish(cancellation.messages)


def handle_cancellation_accepted(repository, bus, event):
    cancellation = repository.get(event.order_id)
    cancellation.accepted()
    bus.publish(cancellation.messages)


def handle_cancellation_rejected(repository, bus, event):
    cancellation = repository.get(event.order_id)
    cancellation.rejected()
    bus.publish(cancellation.messages)


def handle_cancellation_skipped(repository, bus, event):
    cancellation = repository.get(event.order_id)
    cancellation.skip()
    bus.publish(cancellation.messages)
