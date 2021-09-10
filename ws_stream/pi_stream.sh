ffmpeg \
    -f v4l2 \
    -i /dev/video0 \
    -f mpegts \
        -c:v mpeg1video \
        -crf 32 \
        -s 640x480 \
        -framerate 15 \
        -an \
        -b:v 256k \
        -minrate 256k \
        -bufsize 512k \
        -maxrate 512k \
        -bf 0 \
        -preset veryfast \
        -tune zerolatency \
        -movflags +faststart \
        -x264opts no-scenecut \
        udp://localhost:8083
