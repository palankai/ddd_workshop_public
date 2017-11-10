import collections
import json
import threading
import uuid
import sys

import requests



class TopicBasedPubSub:

    def __init__(self):
        self._handlers = collections.defaultdict(tuple)
        self._lock = threading.Lock()

    def publish(self, topic, message):
        for handler in self._handlers[topic]:
            handler(message)
        correlation_id = message.correlation_id
        for handler in self._handlers[correlation_id]:
            handler(message)

    def subscribe(self, topic, handler):
        self._lock.acquire()
        try:
            self._handlers[topic] = self._handlers[topic] + (handler, )
        finally:
            self._lock.release()

    def unsubscribe(self, topic, handler):
        self._lock.acquire()
        try:
            handlers = list(self._handlers[topic])
            handlers.remove(handler)
            if len(handlers) > 0:
                self._handlers[topic] = tuple(handlers)
            else:
                del self._handlers[topic]
        finally:
            self._lock.release()

    def get_info(self):
        return f'BUS: {len(self._handlers)}'



class ESTopicBasedPubSub:

    def __init__(self, eventstore):
        self._handlers = collections.defaultdict(tuple)
        self._lock = threading.Lock()
        self._eventstore = eventstore
        self._running = False

    def publish(self, topic, message):
        requests.post(
            f'{self._eventstore}/streams/orders',
            headers={
                'Content-Type': 'application/json',
                'ES-EventType': topic,
                'ES-EventId': str(uuid.uuid4())
            },
            data=message.serialize()
        )

    def subscribe(self, topic, handler):
        self._lock.acquire()
        try:
            self._handlers[topic] = self._handlers[topic] + (handler, )
        finally:
            self._lock.release()

    def dispatch(self, topic, message):
        for handler in self._handlers[topic]:
            handler(message)

    def dispatch_entry(self, entry):
        topic = entry.event_type
        message = entry.data
        try:
            self.dispatch(topic, message)
        except:
            pass
        pass

    def start(self):
        self._create_permanent_subscription('orders')

        print(entry_collection.entries[0].data)
        sys.exit(0)
        pass

    def run(self):
        assert not self._running
        self._running = True
        while self._running:
            entries = self._read_from_subscription()
            for entry in entries:
                self.dispatch_entry(entry)
        self._running = False

    def stop(self):
        self._running = False

    def _ack_entry(self, entry):
        pass

    def _nack_entry(self, entry):
        pass

    def _create_permanent_subscription(self, stream):
        subscription_name = 'dddws'
        r = requests.put(
            f'{self._eventstore}/subscriptions/{stream}/{subscription_name}',
            headers={
                'Content-Type': 'application/json',
            },
            data=json.dumps({

            }),
            auth=('admin', 'changeit')
        )
        if r.status_code == 409:
            return
        if r.status_code != 201:
            print(r.text)
            sys.exit(-1)

    def _read_from_subscription(self):
        subscription_name = 'dddws'
        stream = 'orders'
        embed = 'body'
        url = f'{self._eventstore}/subscriptions/{stream}/{subscription_name}?embed={embed}'
        print('URL:', url)
        r = requests.get(
            url, 
            headers={
                'Accept': 'application/vnd.eventstore.competingatom+json'
            }
        )
        if r.status_code != 200:
            print(f'***** ERROR {r.status_code} *************')
            print(r.text)
            sys.exit(-1)
        return EntryCollection(r.json())


class EntryCollection:

    def __init__(self, data):
        self._data = data

    @property
    def entries(self):
        return [Entry(entry) for entry in self._data['entries']]

    def __len__(self):
        return len(self.entries)


class Entry:

    def __init__(self, entry):
        self._entry = entry

    @property
    def event_type(self):
        return self._entry['eventType']

    @property
    def position_stream_id(self):
        return self._entry['positionStreamId']

    @property
    def data(self):
        return json.loads(self._entry['data'])

    @property
    def links(self):
        pass


class Link:

    def __init__(self, data):
        self._data = data

    @property
    def uri(self):
        return self._data['uri']

    @property
    def relation(self):
        return self._data['relation']
