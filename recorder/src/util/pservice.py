from multiprocessing import Process, Queue
import logging
import time

import setup_log

logger = logging.getLogger()

class PService(Process):


    def __init__(self, interval=1E9):
        super().__init__(daemon=True)
        self._input_queue = Queue(maxsize=10)
        self._output_queue = Queue(maxsize=10)
        self._update_message = None
        self._interval = interval
        self._set_stop = False
        self._set_update = False
        self._stopped = False
        self._has_started = False


    def update(self, action, message):
        try:
            self._input_queue.put_nowait({'action': action, 'message': message})
        except:
            logger.exception('Update service failed')


    def push(self, data):
        try:
            if not self._output_queue.full():
                self._output_queue.put_nowait(data)
        except:
            pass


    def poll(self, timeout=10):
        try:
            return self._output_queue.get(block=True, timeout=timeout)
        except:
            pass


    def run_start(self):
        pass


    def run_end(self):
        pass


    def run_loop(self):
        pass


    def run_update(self, message):
        pass


    def try_start(self):
        self._has_started = True
        try:
            self.run_start()
            return True
        except:
            logger.exception('Unexpected error in start')
            self._stopped = True
            return False


    def try_loop(self):
        try:
            self.run_loop()
            return True
        except:
            logger.exception('Unexpected error in loop')
            return False


    def try_input(self):
        try:
            if not self._input_queue.empty():
                message = self._input_queue.get_nowait()
                if message is not None:
                    if message.get('action') == 'set_interval':
                        self._interval = message.get('message')
                    elif message.get('action') == 'stop':
                        self._set_stop = True
                    elif message.get('action') == 'update':
                        self._set_update = True
                        self._update_message = message.get('message')
        except:
            logger.exception('Unexpected error in input')


    def try_update(self):
        try:
            if self._set_update:
                self.run_update(self._update_message)
            return True
        except:
            logger.exception('Unexpected error in update')
            return False
        finally:
            self._set_update = False
            self._update_message = None


    def try_sleep(self, start):
        # sleep for 10 ms but constantly check if
        # service would like to stop
        elapsed = time.time_ns() - start
        sleep_time = self._interval - elapsed
        sleep_time = 0 if sleep_time < 0 else sleep_time
        start_sleep = time.time_ns()
        while time.time_ns() - start_sleep <= sleep_time:
            if self._set_stop:
                break
            self.try_input()
            self.try_update()
            time.sleep(0.01)


    def try_end(self):
        try:
            self.run_end()
        except:
            logger.exception('Unexpected error in end')
        finally:
            self._stopped = True


    def run(self):
        setup_log.setup_logger()

        if not self.try_start():
            return

        while not self._set_stop:
            start = time.time_ns()
            self.try_loop()
            self.try_input()
            self.try_update()
            self.try_sleep(start)
        self.try_end()


    def stop(self):
        try:
            self._input_queue.put_nowait({'action': 'stop'})
        except:
            logger.exception('Stop update failed')


    def shutdown(self, timeout=10):
        self.join(timeout=timeout)
        self.kill()


    def is_stopped(self):
        return self._stopped


    def has_started(self):
        return self._has_started