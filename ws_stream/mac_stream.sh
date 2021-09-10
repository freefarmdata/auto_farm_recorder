
ffmpeg \
    -re \
    -an \
    -f avfoundation \
    -pix_fmt yuyv422 \
    -framerate 30 \
    -video_size 640x480 \
    -i "0:0" \
    -threads 4 \
    -vcodec mpeg1video \
    -crf 21 \
    -b:v 512k \
    -minrate 512k \
    -bufsize 768k \
    -maxrate 768k \
    -tune zerolatency \
    -movflags +faststart \
    -x264opts no-scenecut \
    -f tee \
    -map 0:v "[f=segment\:segment_time=30\:reset_timestamps=1\:strftime=1]./biocamcvid45_%s.mp4|[f=mpegts]udp\://127.0.0.1\:8083/"

    
        
