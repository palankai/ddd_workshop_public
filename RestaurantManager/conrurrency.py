import threading


class ThreadProcessor:

    def __init__(self):
        self._running = False

    def run_once(self):
        raise NotImplementedError()

    def run(self):
        assert not self._running
        self._running = True
        while self._running:
            self.run_once()
        self._running = False

    def start(self):
        manager = threading.Thread(target=self.run)
        manager.start()

    def stop(self):
        self._running = False
