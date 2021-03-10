import base64
import cv2

# the last image that was taken
latest_image = None


def set_latest_image(image):
    global latest_image
    comp_settings = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    _, buffer = cv2.imencode('.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    latest_image = str(base64.b64encode(buffer), 'utf-8')


def get_latest_image():
    global latest_image
    if latest_image is None:
        return "", 200
    return latest_image, 200