import os
import datetime
import random
import logging
from concurrent.futures import ThreadPoolExecutor, Future
from collections import deque

from fservice import state
from fservice.tservice import TService
import boto3
import botocore

import controllers.alarms as alarm_controller
from util.file_util import file_is_being_accessed
from util.time_util import profile_func

logger = logging.getLogger()

def create_s3_client():
    session = boto3.Session(profile_name='juser')
    s3_config = botocore.config.Config(
        max_pool_connections=128,
        connect_timeout=5,
        read_timeout=5
    )        
    s3_client = session.client('s3', config=s3_config)

    return s3_config, s3_client

class Uploader(TService):


    def __init__(self):
        super().__init__()
        self.set_interval(1E9)
        self.s3_config, self.s3_client = create_s3_client()
        self.pool = None
        self.queue = None
        self.concurrency = None
        self.futures = {}


    def run_start(self):
        self.concurrency = state.get_service_setting('uploader', 'concurrency')
        self.pool = ThreadPoolExecutor(self.concurrency)
        alarm_controller.clear_alarm('uploader_service_offline')


    def run_loop(self):
        if self.queue is None or len(self.queue) <= 0:
            self.load_queue()
        
        if (
            self.queue is not None
            and len(self.queue) > 0
            and len(self.futures) < self.concurrency
        ):
            file = self.queue.pop()
            future = self.pool.submit(self.upload, file)
            self.futures[future] = file
            future.add_done_callback(self.on_uploaded)


    def run_end(self):
        alarm_controller.set_warn_alarm('uploader_service_offline', 'Uploader Service Is Offline')


    def load_queue(self):
        recordings = self.get_upload_recordings()
        readings = self.get_upload_readings()
        files = [*recordings, *readings]
        random.shuffle(files)
        self.queue = deque(files)


    def get_upload_recordings(self):
        video_dir = state.get_global_setting('video_dir')
        video_files = [os.path.join(video_dir, f) for f in os.listdir(video_dir)]
        video_files = list(filter(lambda f: f.endswith('.mp4'), video_files))
        video_files = list(filter(lambda f: not file_is_being_accessed(f), video_files))
        return video_files


    def get_upload_readings(self):
        archive_dir = state.get_global_setting('archive_dir')
        archive_files = [os.path.join(archive_dir, f) for f in os.listdir(archive_dir)]
        archive_files = list(filter(lambda f: f.endswith('.csv'), archive_files))
        archive_files = list(filter(lambda f: not file_is_being_accessed(f), archive_files))
        return archive_files


    def on_uploaded(self, future):
        file = self.futures[future]
        try:
            future.result()
            if os.path.exists(file):
                os.remove(file)
        except:
            logger.exception(f'failed to upload file: {file}')
        finally:
            del self.futures[future]


    @profile_func(name='uploader_upload')
    def upload(self, file_path):
        bucket_name = state.get_service_setting('uploader', 'bucket_name')
        upload_path = state.get_service_setting('uploader', 'upload_path')
        object_key = os.path.join(upload_path, os.path.basename(file_path))

        logger.info(f'Uploading {file_path} to {object_key}')

        self.s3_client.upload_file(
            Bucket=bucket_name,
            Key=object_key,
            Filename=file_path
        )

        logger.info(f'Successfully uploaded {file_path} to {object_key}')

