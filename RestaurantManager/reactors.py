"""
Reactors should be composed together to achieve the expected
infrastructure.
"""
from conrurrency import ThreadProcessor
import collections
import datetime
import os
import queue
import random
import threading
import time


class Multiplexer:
    """
    Send the message to multiple handlers

            o
            |
            x
           /|\
          / | \
         /  |  \
    ---- --- --- ----
       |_| |_| |_|
    """

    def __init__(self, handlers):
        self._handlers = handlers

    def handle(self, order):
        for h in self._handlers:
            h.handle(order.copy())


class RoundRobinDispatcher:
    """
    Send the incoming message to the next handler

            o
            |
            x
           /
          /
         /
    ---- --- --- ----
       |_| |_| |_|
        ^
    """

    def __init__(self, handlers):
        self._handlers = list(handlers)

    def handle(self, order):
        handler = self._handlers.pop(0)
        self._handlers.append(handler)
        handler.handle(order.copy())


class MoreFairDispatcher:
    """
    Send the incoming message to the next handler
    which has to have a queue, and the queue size
    is under the limit. If none available it waits.

            o
            |
            x
           /
          /
         /
    ---- --- --- ----
       [ ] [ ] [o]
       [ ] [o] [o]
    -> [ ] [o] [o]
       [o] [o] [o]
        ^
    """

    def __init__(self, handlers, limit):
        self._limit = limit
        self._handlers = handlers

    def handle(self, order):
        handler = None
        while handler is None:
            handler = self._pick_one_handler()
        handler.handle(order)

    def _pick_one_handler(self):
        for handler in self._handlers:
            if handler.get_queue_size() < self._limit:
                return handler


class QueueHandler(ThreadProcessor):
    """
    It has a queue and a handler to forward.
    If a new message arrives, it puts in the queue.
    In the same time it forwards the messages one by one
    to the handler synchronously.

            o
           [ ]
           [ ]
           [ ]
           [o]
           [o]
          -- --
           |_|
    """


    def __init__(self, handler, name):
        self._name = name
        self._handler = handler
        self._queue = queue.Queue()
        super().__init__()

    def handle(self, order):
        self._queue.put(order)

    def get_queue_size(self):
        return self._queue.qsize()

    def get_name(self):
        return self._name

    def get_info(self):
        return f'{self.get_name()}: {self.get_queue_size()}'

    def run_once(self):
        try:
            order = self._queue.get(timeout=1)
        except queue.Empty:
            return
        self._handler.handle(order)


class AlarmClock(ThreadProcessor):
    """
    On a given time it send a message to a bus.
    The time specified on the message
            o
            |
            |
    ------------------
     #   #    ### ###
    ##  ##  #   # #
     #   #    ### ###
     #   #  # #   # #
    ### ###   ### ###
    -----------------
            |
            |
            o
    """

    def __init__(self, bus):
        self._messages = []
        self._bus = bus
        super().__init__()

    def handle(self, message):
        when = datetime.datetime.utcnow() + datetime.timedelta(seconds=message.delay)
        self._messages.append((when, message))

    def run_once(self):
        now = datetime.datetime.utcnow()
        for element in list(self._messages):
            when, message = element
            if now > when:
                self._bus.publish(message.topic, message.message)
                self._messages.remove(element)
                print('******* WAKE **********')
        time.sleep(1)



class Chaos:
    """
    This reactor implements the Chaos
    Given the loose and duplicate ratio it decide
    to forward a message twice
    to not to forward the message at all
    to forward it normally

            o
            |
            x
           /|\
          o | \
         o  *  \
    ---- --- --- ----
       |_| |_| |_|

    This shouldn't be added to any production system!
    """

    def __init__(self, handler, loose_ratio=0.3, duplication_ratio=0.4):
        self._handler = handler
        self._loose_ratio = loose_ratio
        self._duplication_ratio = duplication_ratio
        random.seed()

    def handle(self, event):
        rnd = random.random()
        if rnd >= (self._loose_ratio + self._duplication_ratio):
            self._handler.handle(event)
        elif rnd >= self._loose_ratio:
            self._handler.handle(event)
            self._handler.handle(event)


class Monitor(ThreadProcessor):
    """
    It display info about the different reactors
    """

    def __init__(self, handlers):
        self._handlers = handlers
        super().__init__()

    def run_once(self):
        print('*' * 40)
        for handler in self._handlers:
            print('*', handler.get_info())
        print('*' * 40)
        time.sleep(.5)
