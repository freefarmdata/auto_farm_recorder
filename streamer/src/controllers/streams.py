import os

def get_esp32_encoding_pipeling(config: dict, output_directory: str):
  stream_file = os.path.join(output_directory, config.get('stream_name')) + "_%s.mp4"
  file_pipe = f"[f=segment\:segment_time={config.get('segment_time')}\:reset_timestamps=1\:strftime=1]{stream_file}|"
  
  if not config.get('archive'):
    file_pipe = ""

  return f"""ffmpeg \
    -i http://{config.get('ip_address')}:81/stream \
    -an \
    -vsync 2 \
    -threads {config.get('threads')} \
    -vcodec mpeg1video \
    -framerate {config.get('framerate')} \
    -video_size {config.get('video_size')} \
    -crf {config.get('quality')} \
    -b:v {config.get('bitrate')} \
    -minrate {config.get('minrate')} \
    -bufsize {config.get('bufsize')} \
    -maxrate {config.get('maxrate')} \
    -tune zerolatency \
    -movflags +faststart \
    -x264opts no-scenecut \
    -f tee \
    -map 0:v "{file_pipe}[f=mpegts]udp\://{config.get('stream_host')}\:{config.get('stream_port')}/"
  """


def get_pi_usb_encoding_pipeline(config: dict, output_directory: str):
  stream_file = os.path.join(output_directory, config.get('stream_name')) + "_%s.mp4"
  file_pipe = f"[f=segment\:segment_time={config.get('segment_time')}\:reset_timestamps=1\:strftime=1]{stream_file}|"

  if not config.get('archive'):
    file_pipe = ""

  return f"""ffmpeg \
    -f v4l2 \
    -i /dev/video{config.get('video_index')} \
    -an \
    -vsync 2 \
    -threads {config.get('threads')} \
    -vcodec mpeg1video \
    -framerate {config.get('framerate')} \
    -video_size {config.get('video_size')} \
    -crf {config.get('quality')} \
    -b:v {config.get('bitrate')} \
    -minrate {config.get('minrate')} \
    -bufsize {config.get('bufsize')} \
    -maxrate {config.get('maxrate')} \
    -tune zerolatency \
    -movflags +faststart \
    -x264opts no-scenecut \
    -f tee \
    -map 0:v "{file_pipe}[f=mpegts]udp\://{config.get('stream_host')}\:{config.get('stream_port')}/"
  """


def get_mac_webcam_encoding_pipeline(config: dict, output_directory: str):
  stream_file = os.path.join(output_directory, config.get('stream_name')) + "_%s.mp4"
  file_pipe = f"[f=segment\:segment_time={config.get('segment_time')}\:reset_timestamps=1\:strftime=1]{stream_file}|"
  
  if not config.get('archive'):
    file_pipe = ""

  return f"""ffmpeg \
    -re \
    -an \
    -f avfoundation \
    -pix_fmt yuyv422 \
    -framerate {config.get('framerate')} \
    -video_size {config.get('video_size')} \
    -i "0:0" \
    -vsync 2 \
    -threads {config.get('threads')} \
    -vcodec mpeg1video \
    -crf {config.get('quality')} \
    -b:v {config.get('bitrate')} \
    -minrate {config.get('minrate')} \
    -bufsize {config.get('bufsize')} \
    -maxrate {config.get('maxrate')} \
    -tune zerolatency \
    -movflags +faststart \
    -x264opts no-scenecut \
    -f tee \
    -map 0:v "{file_pipe}[f=mpegts]udp\://{config.get('stream_host')}\:{config.get('stream_port')}/"
  """