import cv2

camera = cv2.VideoCapture(1)

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 720)

ret, frame = camera.read()
if ret is True:
  cv2.imwrite('test_camera.png', frame)