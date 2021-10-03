import os
import datetime
import logging
import time

from fservice import state
from fservice.tservice import TService
import boto3

import database

import controllers.alarms as alarm_controller
from util.file_util import file_is_being_accessed
from util.time_util import profile_func

logger = logging.getLogger()

class Archiver(TService):


    def __init__(self):
        super().__init__()
        self.set_interval(10E9)
        self.s3_client = boto3.client('s3')
        self.s3_config = boto3.s3.transfer.TransferConfig(
            max_concurrency=8,
            use_threads=True
        )


    def run_start(self):
        alarm_controller.clear_alarm('archiver_service_offline')


    @profile_func(name='archiver_loop')
    def run_loop(self):
        self.check_oldest_reading()


    @profile_func(name='archiver_update')
    def run_update(self, message):
        if message is not None:
            if message.get('action') == 'archive':
                self.archive_readings(message)
            if message.get('action') == 'delete':
                self.delete_readings(message)


    def run_end(self):
        alarm_controller.set_warn_alarm('archiver_service_offline', 'Archiver Service Is Offline')


    def archive_readings(self, message):
        archive_dir = state.get_global_setting('archive_dir')

        file_name = f'readings_{message.get("start_date")}_{message.get("end_date")}.csv'
        file_path = os.path.join(archive_dir, file_name)

        start_date = datetime.datetime.fromtimestamp(message.get("start_date"))
        end_date = datetime.datetime.fromtimestamp(message.get("end_date"))

        logger.info(f'Archiving readings to disk: {file_name}')
        database.copy_readings_to_disk(file_path, start_date, end_date)


    def delete_readings(self, message):
        start_date = datetime.datetime.fromtimestamp(message.get("start_date"))
        end_date = datetime.datetime.fromtimestamp(message.get("end_date"))

        logger.info(f'Deleting readings from {start_date} to {end_date}')
        database.delete_readings(start_date, end_date)


    def check_oldest_reading(self):
        oldest_reading = database.query_oldest_reading()
        if oldest_reading is not None:
            now = time.time()
            expire_time = state.get_service_setting('archiver', 'expire_time')
            past_due = oldest_reading.get('timestamp') - (now - expire_time)

            logger.info(f'oldest reading past due: {past_due}')

            if past_due < 0:
                past_due_minutes = round(int(abs(past_due)) / 60, 2)

                alarm_controller.set_info_alarm(
                    'archiver_reading_expired',
                    f'Oldest reading is {past_due_minutes} minutes overdue'
                )

