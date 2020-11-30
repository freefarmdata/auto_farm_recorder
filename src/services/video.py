import cv2
import os
import json
import datetime
import time
import logging
from service import Service

logger = logging.getLogger(__name__)

class Video(Service):


    def __init__(self):
        super().__init__()
        self.resolution = (1080, 1920)
        self.data_dir = '/etc/recorder'
        self.image_dir = os.path.join(self.data_dir, 'images')
        self.video_dir = os.path.join(self.data_dir, 'videos')


    def run_start(self):
        self.set_interval(30E9)
        self.setup_data_dirs()


    def setup_data_dirs(self):
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.video_dir, exist_ok=True)


    def run_loop(self):
        images = os.listdir(self.image_dir)
        # 720 = 60 minutes * 12 frames per minute. So 720 frames per hour
        if len(images) >= 720:
            self.make_video(images)


    def make_video(self, images):
        images = sorted(images, key=lambda f: int(f.split('.')[0]))

        first_time = int(images[0].split('.')[0])
        last_time = int(images[-1].split('.')[0])

        video_name = f'{first_time}_{last_time}_{len(images)}'
        video_path = os.path.join(self.video_dir, f"{video_name}.avi")
        timestamp_path = os.path.join(self.video_dir, f"{video_name}.json")

        xvid_encoder = cv2.VideoWriter_fourcc(*'FFV1')
        writer = cv2.VideoWriter(video_path, xvid_encoder, 15, self.resolution)
        timestamps = []

        logger.info(f'Creating video {video_path}')
        for image in images:
            image_time = int(image.split('.')[0])
            image_path = os.path.join(self.image_dir, image)
            frame = cv2.imread(image_path)

            if frame is None or frame.shape[:2] != self.resolution:
                shape = frame.shape if frame is not None else None
                logger.error(f'Cannot write {image_path} to video. Shape: {shape}. Resolution: {self.resolution}')
                continue

            timestamps.append(image_time)
            writer.write(frame)
        writer.release()

        logger.info(f'Creating json timestamps for {timestamp_path}')
        with open(timestamp_path, 'w') as f:
            json.dump(timestamps, f)

        logger.info(f'Removing {len(images)} images')
        for image in images:
            image_path = os.path.join(self.image_dir, image)
            if os.path.isfile(image_path):
                os.remove(image_path)

