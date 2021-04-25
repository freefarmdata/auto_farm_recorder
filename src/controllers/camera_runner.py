import cv2
import time
import logging

from util.pservice import PService

logger = logging.getLogger()

class CameraRunner(PService):


    def __init__(self, resolution, interval):
        super().__init__()
        self.resolution = resolution
        self._interval = interval
        self.camera = None


    def run_start(self):
        self.setup_camera()


    def run_loop(self):
        self.setup_camera()
        try:
            self.capture_image()
        except:
            logger.exception('Failed to capture image')
            self.shutdown_camera()


    def run_update(self, message):
        if message.get('action') == 'resolution':
            self.resolution = message.get('resolution')


    def run_end(self):
        self.shutdown_camera()


    def setup_camera(self):
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
            time.sleep(5)

            if not self.camera.isOpened():
                logger.error('Camera could not be opened')
                self.camera = None
                return

            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])


    def shutdown_camera(self):
        if self.camera:
            self.camera.release()
        self.camera = None

    
    def capture_image(self):
        if self.camera:
            ret, frame = self.camera.read()
            image_time = int(time.time() * 1e3)
            if ret is True and frame is not None:
                if not self._output_queue.full():
                    self._output_queue.put({
                        'data': frame,
                        'time': image_time
                    })

