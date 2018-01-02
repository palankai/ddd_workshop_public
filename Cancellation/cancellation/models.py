from . import messages


class Aggregate:

    def __init__(self):
        self.messages = []


class Cancellation(Aggregate):

    def __init__(self, order_id, state=None):
        self.order_id = order_id
        self.state = state
        super().__init__()

    def requested(self):
        self.request_at_warehouse()

    def rejected(self):
        self.state = 'rejected'

    def accepted(self):
        self.state = 'accepted'

    def skip(self):
        if self.state == 'wait_for_warehouse':
            self.request_at_hacienda()
        elif self.state == 'wait_for_hacienda':
            self.request_at_erp()
        else:
            raise Exception('This should not happen')

    def request_at_warehouse(self):
        self.messages.append(messages.CancelAtWarehouse(order_id=self.order_id))
        self.state = 'wait_for_warehouse'

    def request_at_hacienda(self):
        self.messages.append(messages.CancelAtHacienda(order_id=self.order_id))
        self.state = 'wait_for_hacienda'

    def request_at_erp(self):
        self.messages.append(messages.CancelAtERP(order_id=self.order_id))
        self.state = 'wait_for_erp'
