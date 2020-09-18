import threading
import time

def now_ns():
  return time.time()*1E9

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

  def run(self):
    self._has_started = True
    self.run_start()
    while not self._stop_event.is_set():
      start = now_ns()
      try:
        self.run_loop()
      except Exception as e:
        print(f'Unexpected error in loop: {str(e)}')
      if self._stop_event.is_set():
        break
      if self._update_event.is_set():
        self.run_update()
        self._update_event.clear()
      elapsed = now_ns() - start
      sleep_time = self._interval - elapsed
      sleep_time = 0 if sleep_time < 0 else sleep_time
      start_sleep = now_ns()
      while now_ns() - start_sleep <= sleep_time:
        if self._stop_event.is_set():
          break
        time.sleep(0.1)
      self._tick += 1
    self.run_end()
    self._stopped = True

  def run_loop(self):
    pass

  def run_update(self):
    pass

  def update(self):
    self._update_event.set()

  def stop(self):
    self._stop_event.set()

  def is_stopped(self):
    return self._stopped

  def has_started(self):
    return self._has_started
