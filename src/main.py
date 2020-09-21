import time
import sys
import signal
import state
import api
import database

def signal_handler(sig, frame):
  state.stop_services()
  sys.exit(0)
  exit(0)

if __name__ == "__main__":
  signal.signal(signal.SIGINT, signal_handler)

  print("Ten second delay startup...")
  time.sleep(10)

  database.initialize()
  state.start_services()
  api.start()
  while True:
    time.sleep(100)