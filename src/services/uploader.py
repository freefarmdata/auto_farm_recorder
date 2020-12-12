import cv2
import os
import json
import datetime
import time
import logging
from util.service import Service
import state

import boto3

logger = logging.getLogger(__name__)

class Uploader(Service):


    def __init__(self):
        super().__init__()
        self.data_dir = '/etc/recorder'
        self.video_dir = os.path.join(self.data_dir, 'videos')
        self.bucket_name = 'jam-general-storage'
        self.upload_path = 'datasets/auto_farm/experiment_hawaii_2021/images/'
        self.s3_client = boto3.client('s3')
        self.s3_config = boto3.s3.transfer.TransferConfig(
            max_concurrency=8,
            use_threads=True
        )


    def run_start(self):
        self.set_interval(300E9)
        self.setup_data_dirs()


    def run_loop(self):
        files = self.get_finished_files()
        if len(files) > 0:
            if self.upload(files[0]):
                os.remove(files[0])


    def setup_data_dirs(self):
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.video_dir, exist_ok=True)


    def get_finished_files(self):
        old_files = [os.path.join(self.video_dir, f) for f in os.listdir(self.video_dir)]
        old_files = [[f, os.stat(f).st_size] for f in old_files]
        time.sleep(2)

        static_files = []
        for old_file in old_files:
            new_size = os.stat(old_file[0]).st_size
            if old_file[1] == new_size:
                static_files.append(old_file[0])

        return static_files


    def upload(self, file_path):
        file_name = os.path.basename(file_path)
        object_key = os.path.join(self.upload_path, file_name)

        try:
            logger.info(f'Uploading {file_path} to {object_key}')
            self.s3_client.upload_file(
                Bucket=self.bucket_name,
                Config=self.s3_config,
                Key=object_key,
                Filename=file_path
            )
            return True
        except Exception as e:
            logger.error(f'Failed to upload file {e}')

        return False

