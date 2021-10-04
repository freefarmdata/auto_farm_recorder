import os
import datetime
import logging
import time

from fservice import state
from fservice.tservice import TService
import boto3

import database

import controllers.settings as settings_controller
import controllers.alarms as alarm_controller
from util.time_util import profile_func, sec_to_date, get_daynight_schedule

logger = logging.getLogger()

class Archiver(TService):


    def __init__(self):
        super().__init__()
        self.set_interval(30E9)
        self.sunrise, self.sunset = get_daynight_schedule(
            state.get_global_setting('sunrise'),
            state.get_global_setting('sunset')
        )


    def run_start(self):
        alarm_controller.clear_alarm('archiver_service_offline')


    @profile_func(name='archiver_loop')
    def run_loop(self):
        if self.should_archive():
            last_archive = self.get_archive_date()
            if self.archive_readings(last_archive):
                alarm_controller.set_info_alarm(
                    'archiver_processed',
                    f'Archive processed on {sec_to_date(last_archive).strftime("%Y-%m-%d")}'
                )
                state.set_service_setting('archiver', 'last_archive', last_archive)
                settings_controller.save_settings()


    def run_end(self):
        alarm_controller.set_warn_alarm('archiver_service_offline', 'Archiver Service Is Offline')


    def get_archive_date(self):
        start_date = state.get_global_setting('start_date')
        last_archive = state.get_service_setting('archiver', 'last_archive')

        # if never archived, set the archive date to the start_date
        if last_archive is None:
            last_archive = start_date

        # if archived, uptick the date by 1 day
        else:
            last_archive = sec_to_date(last_archive)
            last_archive += datetime.timedelta(days=1)
            last_archive = last_archive.timestamp()
        
        return last_archive


    def should_archive(self):
        if self.is_daytime():
            return False

        now = time.time()
        start_date = state.get_global_setting('start_date')
        expire_time = state.get_service_setting('archiver', 'expire_time')
        last_archive = state.get_service_setting('archiver', 'last_archive')

        # never archived, but need to start archiving now
        if (
            last_archive is None 
            and now - start_date >= expire_time
        ):
            return True

        # has archived, and last archive date is still more than expire time
        if (
            last_archive is not None
            and now - last_archive >= expire_time
        ):
            return True

        return False


    def is_daytime(self):
        current_time = datetime.datetime.now().time()
        later = current_time >= self.sunrise
        early = current_time <= self.sunset
        return later and early


    def archive_readings(self, last_archive):
        try:
            archive_dir = state.get_global_setting('archive_dir')

            start_date = last_archive
            end_date = sec_to_date(start_date) + datetime.timedelta(days=1)
            end_date = end_date.timestamp()

            file_name = f'readings_{int(start_date)}_{int(end_date)}.csv'
            file_path = os.path.abspath(os.path.join(archive_dir, file_name))

            start_date = datetime.datetime.fromtimestamp(start_date)
            end_date = datetime.datetime.fromtimestamp(end_date)

            logger.info(f'Archiving readings to disk: {file_name}')
            database.copy_readings_to_disk(file_path, start_date, end_date)

            return True
        except:
            logger.exception(f'failed to archive on {last_archive}')


    # def delete_readings(self, message):
    #     start_date = datetime.datetime.fromtimestamp(message.get("start_date"))
    #     end_date = datetime.datetime.fromtimestamp(message.get("end_date"))

    #     logger.info(f'Deleting readings from {start_date} to {end_date}')
    #     database.delete_readings(start_date, end_date)


    # def check_oldest_reading(self):
    #     oldest_reading = database.query_oldest_reading()
    #     if oldest_reading is not None:
    #         now = time.time()
    #         expire_time = state.get_service_setting('archiver', 'expire_time')
    #         past_due = oldest_reading.get('timestamp') - (now - expire_time)

    #         logger.info(f'oldest reading past due: {past_due}')

    #         if past_due < 0:
    #             past_due_minutes = round(int(abs(past_due)) / 60, 2)

    #             alarm_controller.set_info_alarm(
    #                 'archiver_reading_expired',
    #                 f'Oldest reading is {past_due_minutes} minutes overdue'
    #             )

