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
        if not os.path.isdir(self.data_dir):
            os.mkdir(self.data_dir)

        if not os.path.isdir(self.image_dir):
            os.mkdir(self.image_dir)


    def run_loop(self):
        images = os.listdir(self.image_dir)
        # 720 = 60 minutes * 12 frames per minute. So 720 frames per hour
        if len(images) >= 720:
            self.make_video(images)


    def make_video(self, images):
        images = sorted(images, key=lambda f: int(f.split('.')[0]))
        ffv1_encoder = cv2.VideoWriter_fourcc(*'FFV1')

        video_name = f'{images[0]}_{images[-1]}_{len(images)}'
        video_path = os.path.join(self.video_dir, video_name)
        timestamp_path = os.path.join(self.video_dir, video_name)
        writer = cv2.VideoWriter(video_path, ffv1_encoder, 15, self.resolution)
        timestamps = []

        logger.error(f'Creating video {video_path}')
        for image in images:
            image_time = int(image.split('.')[0])
            image_path = os.path.join(self.image_dir, image)
            frame = cv2.imread(image_path)

            if frame is None or frame.shape[:2] is not self.resolution:
                logger.error(f'Cannot write {image_path} to video')
                continue

            timestamps.append(image_time)
            writer.write(frame)
        writer.release()

        logger.error(f'Creating json timestamps for {video_path}')
        with open(timestamp_path, 'w') as f:
            json.dump(timestamps, f)

        logger.error(f'Removing {len(images)} images')
        for image in images:
            image_path = os.path.join(self.image_dir, image)
            os.remove(image)

