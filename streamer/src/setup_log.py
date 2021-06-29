import sys
import logging

def setup_logger(debug=False):
  logging.getLogger("urllib3").setLevel(logging.ERROR)
  logging.getLogger("requests").setLevel(logging.ERROR)
  logging.getLogger("boto").setLevel(logging.ERROR)
  logging.getLogger("boto3").setLevel(logging.ERROR)
  logging.getLogger("botocore").setLevel(logging.ERROR)
  logging.getLogger('s3transfer').setLevel(logging.ERROR)

  logger = logging.getLogger()

  if debug:
    logger.setLevel(logging.DEBUG)
  else:
    logger.setLevel(logging.INFO)

  formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s - %(message)s', datefmt="%Y-%m-%dT%H:%M:%S%z")
  stream_handler = logging.StreamHandler(sys.stdout)
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)

  return logger
