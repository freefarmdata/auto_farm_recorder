import time
import signal
import state

run_program = True

def signal_handler(sig, frame):
  global run_program
  run_program = False

if __name__ == "__main__":
  signal.signal(signal.SIGINT, signal_handler)

  state.start_services()
  while run_program:
    time.sleep(0.1)
  state.stop_services()