import time
import threading
from collections import deque

from fservice import state

_readings_queue = deque(maxlen=100)

_reading_lock = threading.Lock()

def push_readings(readings=[]):
  global _readings_queue
  with _reading_lock:
    for reading in readings:
      _readings_queue.appendleft(reading)
      state.update_trigger('board_relay')


def pop_reading():
  global _readings_queue
  with _reading_lock:
    return _readings_queue.pop()


