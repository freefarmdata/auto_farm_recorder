from multiprocessing import Queue
import threading
import time
import cv2

_image_lock = threading.Lock()

# the last image that was taken
latest_image = {
    'image': None,
    'time': None,
}

# queue that is triggered when latest image is refreshed
# used by Flask to get live stream
image_queue = Queue(maxsize=5)


def set_latest_image(image, time):
    global latest_image, image_queue

    with _image_lock:
        latest_image['image'] = image
        latest_image['time'] = time

    if not image_queue.full():
        image_queue.put_nowait(None)


def generator():
    global latest_image_queue, latest_image
    comp_settings = [int(cv2.IMWRITE_JPEG_QUALITY), 30]
    while True:
        if not image_queue.empty():
            image_queue.get(block=True)
            with _image_lock:
                buffer = latest_image['image']
                flag, buffer = cv2.imencode('.jpg', buffer, comp_settings)

                if flag:
                    buffer = buffer.tobytes()

                    yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + buffer + b'\r\n')