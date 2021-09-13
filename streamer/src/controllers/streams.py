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
    -framerate {config.get('sfps')} \
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


def get_stereo_usb_encoding_pipeline(config: dict, output_directory: str):
  stream_file = os.path.join(output_directory, config.get('stream_name')) + "_%s.mp4"
  file_pipe = f"[f=segment\:segment_time={config.get('segment_time')}\:reset_timestamps=1\:strftime=1]{stream_file}|"
  udp_pipe = f"[f=mpegts]udp\://{config.get('stream_host')}\:{config.get('stream_port')}/"

  if not config.get('archive'):
    file_pipe = ""

  return f"""ffmpeg \
    -an \
    -f v4l2 \
    -framerate {config.get('infps')} \
    -video_size {config.get('video_size')} \
    -i /dev/video{config.get('video_index')} \
    -f mpegts \
    -vcodec mpeg1video \
    -b:v {config.get('bitrate')} \
    -s {config.get('video_size')} \
    -bf 0 \
    -f tee -map 0:v "{file_pipe}{udp_pipe}"
  """


def get_pi_usb_encoding_pipeline(config: dict, output_directory: str):
  stream_file = os.path.join(output_directory, config.get('stream_name')) + "_%s.mp4"
  file_pipe = f"[f=segment\:segment_time={config.get('segment_time')}\:reset_timestamps=1\:strftime=1]{stream_file}|"
  video_filter = ""

  if not config.get('archive'):
    file_pipe = ""

  if config.get('grayscale') or config.get('outfps'):
    video_filter = "-vf "
    filters = []

    if config.get('grayscale'):
      filters.append("format=gray")
    if config.get('outfps'):
      filters.append(f"fps={config.get('outfps')}")

    video_filter += f'"{" , ".join(filters)}" '

  return f"""ffmpeg \
    -an \
    -f v4l2 \
      -framerate {config.get('infps')} \
      -video_size {config.get('video_size')} \
      -i /dev/video{config.get('video_index')} \
    -f mpegts
      -vcodec mpeg1video \
      -vsync {config.get('vsync')} {video_filter}\
      -threads {config.get('threads')} \
      -crf {config.get('quality')} \
      -b:v {config.get('bitrate')} \
      -minrate {config.get('minrate')} \
      -bufsize {config.get('bufsize')} \
      -maxrate {config.get('maxrate')} \
      -tune zerolatency \
      -movflags +faststart \
      -x264opts no-scenecut \
    -f tee \
    -map 0:v "{file_pipe}udp\://{config.get('stream_host')}\:{config.get('stream_port')}/"
  """


def get_mac_webcam_encoding_pipeline(config: dict, output_directory: str):
  stream_file = os.path.join(output_directory, config.get('stream_name')) + "_%s.mp4"
  file_pipe = f"[f=segment\:segment_time={config.get('segment_time')}\:reset_timestamps=1\:strftime=1]{stream_file}|"
  video_filter = ""

  if not config.get('archive'):
    file_pipe = ""

  if config.get('grayscale') or config.get('fps'):
    video_filter = "-vf "
    filters = []

    if config.get('grayscale'):
      filters.append("format=gray")
    if config.get('fps'):
      filters.append(f"fps={config.get('fps')}")

    video_filter += f'"{" , ".join(filters)}" '

  return f"""ffmpeg \
    -re \
    -an \
    -f avfoundation \
    -pix_fmt yuyv422 \
    -framerate {config.get('framerate')} \
    -video_size {config.get('video_size')} \
    -i "0:0" \
    -vcodec mpeg1video \
    -vsync {config.get('vsync')} {video_filter} \
    -threads {config.get('threads')} \
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