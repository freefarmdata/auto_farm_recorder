import os

def clean_up_stream(name: str, output: str):
  """
  Removes all references to the HLS playlist for the
  given stream name
  """
  files = filter(lambda f: f.startswith(name), os.listdir(output))
  for file_name in files:
    os.remove(os.path.join(output, file_name))


def get_mac_webcam_input():
  return f"""\
  -re \
  -f avfoundation \
  -pix_fmt yuyv422 \
  -framerate 15 \
  -i "0:0" \
  """

def get_encoding_pipeline(options: dict):
    # -vprofile baseline \
    # -fflags nobuffer \
    # -vcodec h264 \
    # -crf {options.get('crf')} \
    # -vf "drawtext=text='%{{localtime\: {name} --- %m/%d/%Y %I.%M.%S %p}}':fontsize=10:fontcolor=white@0.8:x=10:y=10:shadowcolor=red@0.6:shadowx=1:shadowy=1" \

    return f"""\
    -preset veryfast \
    -tune zerolatency \
    -pix_fmt yuv420p \
    -movflags +faststart \
    -x264opts no-scenecut \
    -vsync {options.get('vsync', 1)} \
    -video_size {options.get('video_size', '800x600')} \
    -bufsize {options.get('bufsize', '512k')} \
    -minrate {options.get('minrate', '512k')} \
    -maxrate {options.get('maxrate', '1M')} \
    -framerate {options.get('framerate', 15)} \
    -force_key_frames "expr:gte(t,n_forced*1)" \
    -keyint_min {options.get('keyint_min', 120)} \
    -g {options.get('g', 120)} \
    """

def get_hls_output_pipeline(options: dict, output_file: str):
    return f"""\
    -f hls \
    -hls_flags delete_segments \
    -hls_segment_type mpegts \
    -hls_allow_cache 0 \
    -hls_list_size {options.get('hls_list_size', 1)} \
    -hls_time {options.get('hls_time', 1)} \
    {output_file} \
    """