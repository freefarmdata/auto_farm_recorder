import subprocess
import time
import numpy
import cv2

if __name__ == "__main__":

    options = {}

#    -bufsize {options.get('bufsize', '512k')} \
#     -minrate {options.get('minrate', '512k')} \
#     -maxrate {options.get('maxrate', '1M')} \
#     -framerate {options.get('framerate', 15)} \
#     -force_key_frames "expr:gte(t,n_forced*1)" \
#     -keyint_min {options.get('keyint_min', 120)} \
#     -g {options.get('g', 120)} \
#     -f hls \
#     -hls_flags delete_segments \
#     -hls_segment_type mpegts \
#     -hls_allow_cache 0 \
#     -hls_list_size {options.get('hls_list_size', 1)} \
#     -hls_time {options.get('hls_time', 1)} \
#     ./bin/recorder/streams/test_cam.m3u8 \
# -pix_fmt yuv420p \


#

    command = f"""\
    ffmpeg \
    -re \
    -f avfoundation \
    -an \
    -sn \
    -framerate 15 \
    -i "0:0" \
    -video_size {options.get('video_size', '800x600')} \
    -f rawvideo \
    -pix_fmt bgr24 - \
    """

    cv2.startWindowThread()
    cv2.namedWindow('stream', cv2.WINDOW_AUTOSIZE | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
    cv2.resizeWindow('stream', 800, 600)
    cv2.moveWindow('stream', 0, 0)

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, bufsize=10**8)

    read_buf = 800*600*3
    while not process.poll():
        image = process.stdout.read(read_buf)

        if len(image) <= 0:
            continue

        image = numpy.frombuffer(image, dtype='uint8')
        image = image.reshape((600,800,3))
            

        if image is not None:
            cv2.imshow('stream', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        process.stdout.flush()

    cv2.destroyAllWindows()
