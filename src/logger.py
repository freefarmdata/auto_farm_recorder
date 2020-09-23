import sys
import logging

def setup_logger():
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)

  formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s - %(message)s', datefmt="%Y-%m-%dT%H:%M:%S%z")
  stream_handler = logging.StreamHandler(sys.stdout)
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)

  return logger
