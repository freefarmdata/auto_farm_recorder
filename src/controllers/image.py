import base64
import cv2

# the last image that was taken
latest_image = {
    'image': None,
    'time': None,
}


def set_latest_image(image, time):
    global latest_image
    comp_settings = [int(cv2.IMWRITE_JPEG_QUALITY), 30]
    _, buffer = cv2.imencode('.jpg', image, comp_settings)
    latest_image['image'] = str(base64.b64encode(buffer), 'utf-8')
    latest_image['time'] = time


def get_latest_image():
    global latest_image
    return latest_image