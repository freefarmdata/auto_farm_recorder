import threading
import logging
import time

def now_ns():
    return time.time()*1E9

logger = logging.getLogger(__name__)

class Service(threading.Thread):


    def __init__(self, interval=1E9):
        super().__init__(daemon=True)
        self._stop_event = threading.Event()
        self._update_event = threading.Event()
        self._interval = interval
        self._stopped = False
        self._has_started = False
        self._tick = 0


    def set_interval(self, interval):
        self._interval = interval


    def get_tick(self):
        return self._tick


    def run_start(self):
        pass


    def run_end(self):
        pass


    def run_loop(self):
        pass


    def run_update(self):
        pass


    def try_start(self):
        self._has_started = True
        try:
            self.run_start()
            return True
        except Exception as e:
            logger.error(f'Unexpected error in start: {str(e)}')
            self._stopped = True
            return False


    def try_loop(self):
        try:
            self.run_loop()
            return True
        except Exception as e:
            logger.error(f'Unexpected error in loop: {str(e)}')
            return False


    def try_update(self):
        try:
            if self._update_event.is_set():
                self.run_update()
                self._update_event.clear()
            return True
        except Exception as e:
            logger.error(f'Unexpected error in update: {str(e)}')
            return False


    def try_sleep(self, start):
        # sleep for 100 ms but constantly check if
        # service would like to stop
        elapsed = now_ns() - start
        sleep_time = self._interval - elapsed
        sleep_time = 0 if sleep_time < 0 else sleep_time
        start_sleep = now_ns()
        while now_ns() - start_sleep <= sleep_time:
            if self._stop_event.is_set():
                break
            time.sleep(0.1)


    def try_end(self):
        try:
            self.run_end()
        except Exception as e:
            logger.error(f'Unexpected error in end: {str(e)}')
        self._stopped = True


    def run(self):
        if not self.try_start():
            return

        while not self._stop_event.is_set():
            start = now_ns()
            self.try_loop()
            if self._stop_event.is_set():
                break
            self.try_update()
            self.try_sleep(start)
            self._tick += 1
        self.try_end()


    def update(self):
        self._update_event.set()


    def stop(self):
        self._stop_event.set()


    def is_stopped(self):
        return self._stopped


    def has_started(self):
        return self._has_started