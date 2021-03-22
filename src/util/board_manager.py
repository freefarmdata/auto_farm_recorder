import re
import os
import serial
import json
import time
import logging

logger = logging.getLogger(__name__)

class Board():
    def __init__(self, id, path):
        self.id = id
        self.path = path
        self.baudrate = 9600
        self.timeout = 10
        self.serial = None


    def read(self):
        messages = []
        self.reconnect()
        try:
            if self.serial:
                output = self.serial.read(1000).decode("utf-8")
                output = [l.strip() for l in output.split('\n')]
                for line in output:
                    try:
                        messages.append(json.loads(line))
                    except Exception as e:
                        pass
        except Exception as e:
            logger.error(f'Failed to read from board {self.path}. Error: {e}')
            self.disconnect()
        return messages


    def reconnect(self):
        try:
            if self.serial is None:
                self.serial = serial.Serial(self.path, baudrate=self.baudrate, timeout=self.timeout)
        except Exception as e:
            logger.error(f'Failed to connect to board: {str(e)}')
            self.disconnect()


    def disconnect(self):
        if self.serial:
            self.serial.close()
        self.serial = None


class BoardManager():


    def __init__(self):
        self.boards = []


    def detect(self):
        self.reset()
        devs = [os.path.join('/dev', d) for d in os.listdir('/dev')]
        devs = list(filter(lambda d: re.search('ttyUSB', d), devs))
        devices = []
        logger.info(f'usb devices found: {devs}')
        for dev_path in devs:
            messages = self.test_read_retry(dev_path, retry=3)
            if messages and len(messages) > 0:
                if 'id' in messages[0]:
                    logger.info(f"Board at {dev_path} with id {messages[0]['id']} detected!")
                    devices.append(Board(messages[0]['id'], dev_path))
        self.boards = devices

        if len(self.boards) <= 0:
            logger.error('No auto farm boards detected!')


    def reset(self):
        for board in self.boards:
            board.disconnect()
        self.boards = []


    def test_read_retry(self, dev_path, retry=1):
        for _ in range(retry):
            messages = self.test_read(dev_path)
            if len(messages) > 0:
                return messages


    def test_read(self, dev_path):
        messages = []
        board = None
        try:
            board = serial.Serial(dev_path, baudrate=9600, timeout=2)
            time.sleep(3)
            output = board.read(1000).decode("utf-8")
            logger.info(f'usb device {dev_path} read "{output}"')
            splits = list(map(lambda l: l.strip(), output.split('\n')))
            for line in splits:
                try:
                    messages.append(json.loads(line))
                except Exception as e:
                    pass
        except Exception as e:
            logger.error(f'Failed to test read from {dev_path}. Error: {e}')
        finally:
            if board:
                board.close()

        return messages


    def read(self):
        messages = []
        for board in self.boards:
            messages += board.read()
        return messages
