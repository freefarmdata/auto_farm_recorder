import cv2
import os
import json
import datetime
import time
import logging

import state
from util.service import Service
from util.file_util import file_is_being_accessed

logger = logging.getLogger(__name__)

class Video(Service):


    def __init__(self):
        super().__init__()
        self.set_interval(120E9)


    def run_loop(self):
        if state.get_global_setting('devmode') or not self.is_daytime():
            images = self.get_finished_images()
            if len(images) > 2:
                self.make_video(images)

    
    def get_finished_images(self):
        image_files = os.listdir(state.get_global_setting('image_dir'))
        image_files = list(filter(lambda f: f.endswith('.png'), image_files))
        image_files = list(filter(lambda f: not file_is_being_accessed(f), image_files))
        return image_files


    def is_daytime(self):
        current_time = datetime.datetime.now().time()
        later = current_time >= state.get_global_setting('sunrise')
        early = current_time <= state.get_global_setting('sunset')
        return later and early


    def make_video(self, images):
        # sort the provided images by timestamp
        images = sorted(images, key=lambda f: int(f.split('.')[0]))

        # build the video name from the first and last times
        first_time = int(images[0].split('.')[0])
        last_time = int(images[-1].split('.')[0])
        temp_dir = state.get_global_setting('temp_dir')
        video_name = f'{first_time}_{last_time}_{len(images)}'
        temp_video_path = os.path.join(temp_dir, f"{video_name}.avi")
        temp_times_path = os.path.join(temp_dir, f"{video_name}.json")

        # remove the video if already exists
        if os.path.isfile(temp_video_path):
            logger.info(f'{temp_video_path} already exists. Removing...')
            os.remove(temp_video_path)
        
        # remove the json if already exists
        if os.path.isfile(temp_times_path):
            logger.info(f'{temp_times_path} already exists. Removing...')
            os.remove(temp_times_path)

        # set up the video writer
        image_dir = state.get_global_setting('image_dir')
        resolution = state.get_service_setting('camera', 'resolution')
        if state.get_global_setting('devmode'):
            first_image = cv2.imread(os.path.join(image_dir, images[0]), cv2.IMREAD_COLOR)
            height, width, _ = first_image.shape
            resolution = (width, height)
        
        encoder = cv2.VideoWriter_fourcc(*'FFV1')
        writer = cv2.VideoWriter(temp_video_path, encoder, 1, resolution)
        timestamps = []

        # from all the frames listed and sorted, create the video
        logger.info(f'Creating video {temp_video_path}')
        for image in images:
            image_time = int(image.split('.')[0])
            image_path = os.path.join(image_dir, image)
            frame = cv2.imread(image_path, cv2.IMREAD_COLOR)

            if frame is None:
                logger.error(f'Cannot write {image_path} to video')
                continue

            logger.debug(f'Writing {image_path} to {temp_video_path}')
            logger.debug(f'{image_path} shape: {frame.shape}')

            timestamps.append(image_time)
            writer.write(frame)
        writer.release()

        # dump the timestamps to a json file
        logger.info(f'Creating json timestamps for {temp_times_path}')
        with open(temp_times_path, 'w') as f:
            json.dump(timestamps, f)

        # move temp video and json to video directory to be uploaded
        video_dir = state.get_global_setting('video_dir')
        new_video_path = os.path.join(video_dir, f"{video_name}.avi")
        new_times_path = os.path.join(video_dir, f"{video_name}.json")
        os.rename(temp_video_path, new_video_path)
        os.rename(temp_times_path, new_times_path)

        # if all that is successful, remove images
        logger.info(f'Removing {len(images)} images')
        for image in images:
            image_path = os.path.join(image_dir, image)
            if os.path.isfile(image_path):
                os.remove(image_path)

