import cv2
import os
import json
import datetime
import time
import logging
from util.service import Service

logger = logging.getLogger(__name__)

class Video(Service):


    def __init__(self):
        super().__init__()
        self.resolution = (1920, 1080)
        self.sunrise = datetime.time(6, 0, 0, 0)
        self.sunset = datetime.time(18, 0, 0, 0)
        self.data_dir = '/etc/recorder'
        self.image_dir = os.path.join(self.data_dir, 'images')
        self.temp_dir = os.path.join(self.data_dir, 'temp')
        self.video_dir = os.path.join(self.data_dir, 'videos')


    def run_start(self):
        self.set_interval(120E9)
        self.setup_data_dirs()


    def setup_data_dirs(self):
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.video_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)


    def run_loop(self):
        if not self.is_daytime():
            images = os.listdir(self.image_dir)
            if len(images) >= 0:
                self.make_video(images)


    def is_daytime(self):
        current_time = datetime.datetime.now().time()
        return current_time >= self.sunrise and current_time <= self.sunset


    def make_video(self, images):
        images = sorted(images, key=lambda f: int(f.split('.')[0]))

        first_time = int(images[0].split('.')[0])
        last_time = int(images[-1].split('.')[0])

        video_name = f'{first_time}_{last_time}_{len(images)}'
        video_path = os.path.join(self.temp_dir, f"{video_name}.avi")
        times_path = os.path.join(self.temp_dir, f"{video_name}.json")

        if os.path.isfile(video_path):
            logger.info(f'{video_path} already exists. Removing...')
            os.remove(video_path)
        
        if os.path.isfile(times_path):
            logger.info(f'{times_path} already exists. Removing...')
            os.remove(times_path)

        encoder = cv2.VideoWriter_fourcc(*'FFV1')
        writer = cv2.VideoWriter(video_path, encoder, 1, self.resolution)
        timestamps = []

        logger.info(f'Creating video {video_path}')
        for image in images:
            image_time = int(image.split('.')[0])
            image_path = os.path.join(self.image_dir, image)
            frame = cv2.imread(image_path)

            if frame is None:
                logger.error(f'Cannot write {image_path} to video')
                continue

            timestamps.append(image_time)
            writer.write(frame)
        writer.release()

        logger.info(f'Creating json timestamps for {times_path}')
        with open(times_path, 'w') as f:
            json.dump(timestamps, f)

        logger.info(f'Removing {len(images)} images')
        for image in images:
            image_path = os.path.join(self.image_dir, image)
            if os.path.isfile(image_path):
                os.remove(image_path)

        new_video_path = os.path.join(self.video_dir, f"{video_name}.avi")
        new_times_path = os.path.join(self.video_dir, f"{video_name}.json")
        os.rename(video_path, new_video_path)
        os.rename(times_path, new_times_path)

