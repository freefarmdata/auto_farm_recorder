from threading import Thread, Lock
import subprocess
import logging
import time
import os

import cv2

from flask import Flask, Response
from flask.helpers import send_file
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/*":{"origins":"*"}})

# -break_non_keyframes 1 \
# -write_empty_segments 1 \

def build_archive_pipeline(fps, width, height):
    return f"""
    ffmpeg \
        -y \
        -f rawvideo \
        -vcodec rawvideo \
        -s {width}x{height} \
        -r {fps} \
        -pix_fmt bgr24 \
        -i - \
        -an \
        -vcodec mpeg4 \
        -b:v 1M \
        -map 0 \
        -f segment \
        -segment_time 5 \
        -segment_format mp4 \
        -reset_timestamps 1 \
        -strftime 1 \
        biocamcvid45_%s.mp4
    """

class Stream(Thread):

    def __init__(self):
        super().__init__(daemon=True)
        self.frame = None
        self.lock = Lock()
    

    def run(self):
        fps = 5
        capture = cv2.VideoCapture(0)
        capture.set(cv2.CAP_PROP_FPS, fps)

        time.sleep(2)

        pipeline = None
        success, frame = capture.read()
        if success and frame is not None:
            height, width, _ = frame.shape
            pipeline = build_archive_pipeline(fps, width, height)

        archive_pipe = subprocess.Popen(pipeline, shell=True, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL)

        while True:
            success, frame = capture.read()

            if success and frame is not None:
                archive_pipe.stdin.write(frame.tobytes())
                success, encoded = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 10])

                with self.lock:
                    self.frame = encoded


    def generate(self):
        while True:
            with self.lock:
                if self.frame is None:
                    continue

                yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                    bytearray(self.frame) + b'\r\n')


stream = Stream()

@app.route("/cvstream")
def video_feed():
	return Response(
        response=stream.generate(),
		mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/")
def web():
    return send_file('test_cvstream.html')

if __name__ == "__main__":
    stream.start()
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
