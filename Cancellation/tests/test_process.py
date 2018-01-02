from uuid import uuid4

from expects import be_empty, contain_only, equal, expect

from ..cancellation import infrastructure, messages, handlers, models


class When_a_new_cancellation_process_is_started:

    def given_an_repository(self):
        self.repository = infrastructure.Repository()
        self.bus = infrastructure.Bus()

        self.order_id = "order-123"

    def because_we_process_a_cancellation_started_event(self):
        handlers.handle_cancellation_requested(
            self.repository, self.bus, messages.CancellationRequested(order_id=self.order_id)
        )

    def it_should_raise_cancel_at_warehouse(self):
        expect(self.bus.messages).to(
            contain_only(
                messages.CancelAtWarehouse(self.order_id)
            )
        )

    def it_should_create_the_cancellation_process(self):
        cancellation = self.repository.get(self.order_id)
        expect(cancellation.order_id).to(equal(self.order_id))


class When_the_warehouse_service_approves_the_command:

    def given_a_cancellation(self):
        self.order_id = "order-123"
        self.repository = infrastructure.Repository({
            self.order_id: models.Cancellation(order_id=self.order_id, state='wait_for_warehouse')
        })
        self.bus = infrastructure.Bus()

    def because_the_warehouse_says_yep(self):
        handlers.handle_cancellation_accepted(
            self.repository, self.bus, messages.CancellationAccepted(order_id=self.order_id)
        )

    def it_should_create_the_cancellation_process(self):
        cancellation = self.repository.get(self.order_id)
        expect(cancellation.state).to(equal('accepted'))


class When_the_warehouse_service_rejects_the_command:

    def given_a_cancellation(self):
        self.order_id = "order-123"
        self.repository = infrastructure.Repository({
            self.order_id: models.Cancellation(order_id=self.order_id, state='wait_for_warehouse')
        })
        self.bus = infrastructure.Bus()

    def because_the_warehouse_says_nope(self):
        handlers.handle_cancellation_rejected(
            self.repository, self.bus, messages.CancellationRejected(order_id=self.order_id)
        )

    def it_should_create_the_cancellation_process(self):
        cancellation = self.repository.get(self.order_id)
        expect(cancellation.state).to(equal('rejected'))


class When_the_warehouse_service_skips_the_command:

    def given_a_cancellation(self):
        self.order_id = "order-123"
        self.repository = infrastructure.Repository({
            self.order_id: models.Cancellation(order_id=self.order_id, state='wait_for_warehouse')
        })
        self.bus = infrastructure.Bus()

    def because_the_warehouse_says_wat(self):
        handlers.handle_cancellation_skipped(
            self.repository, self.bus, messages.CancellationSkipped(order_id=self.order_id)
        )

    def it_should_raise_cancel_at_hacienda(self):
        expect(self.bus.messages).to(
            contain_only(
                messages.CancelAtHacienda(self.order_id)
            )
        )


class When_the_hacienda_skips_the_command:

    def given_a_cancellation(self):
        self.order_id = "order-123"
        self.repository = infrastructure.Repository({
            self.order_id: models.Cancellation(order_id=self.order_id, state='wait_for_hacienda')
        })
        self.bus = infrastructure.Bus()

    def because_the_warehouse_says_wat(self):
        handlers.handle_cancellation_skipped(
            self.repository, self.bus, messages.CancellationSkipped(order_id=self.order_id)
        )

    def it_should_raise_cancel_at_hacienda(self):
        expect(self.bus.messages).to(
            contain_only(
                messages.CancelAtERP(self.order_id)
            )
        )
