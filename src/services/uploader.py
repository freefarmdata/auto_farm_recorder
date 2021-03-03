import cv2
import os
import json
import datetime
import time
import logging

from util.file_util import file_is_being_accessed
from util.service import Service
import state

import boto3

logger = logging.getLogger(__name__)

class Uploader(Service):


    def __init__(self):
        super().__init__()
        self.set_interval(10E9)
        self.s3_client = boto3.client('s3')
        self.s3_config = boto3.s3.transfer.TransferConfig(
            max_concurrency=8,
            use_threads=True
        )


    def run_loop(self):
        video_files = self.get_finished_videos()
        if len(video_files) > 0:
            if self.upload(video_files[0]):
                os.remove(video_files[0])


    def get_finished_videos(self):
        video_dir = self.get_setting('video_dir')
        video_files = [os.path.join(video_dir, f) for f in os.listdir(video_dir)]
        video_files = list(filter(lambda f: f.endswith('.json') or f.endswith('.avi'), video_files))
        video_files = list(filter(lambda f: not file_is_being_accessed(f), video_files))
        return video_files


    def upload(self, file_path):
        bucket_name = self.get_setting('bucket_name')
        upload_path = self.get_setting('upload_path')
        file_name = os.path.basename(file_path)
        object_key = os.path.join(upload_path, file_name)

        try:
            logger.info(f'Uploading {file_path} to {object_key}')

            if not self.get_setting('devmode'):
                self.s3_client.upload_file(
                    Bucket=bucket_name,
                    Config=self.s3_config,
                    Key=object_key,
                    Filename=file_path
                )
            logger.info(f'Successfully uploaded {file_path} to {object_key}')
            return True
        except:
            logger.exception('Failed to upload file')

        return False

