from threading import Thread
import logging
import os

from flask import Flask, send_from_directory, send_file
from flask_cors import CORS

from util.no_cache import no_cache
import state

app = Flask(__name__)
cors = CORS(app, resources={r"/*":{"origins":"*"}})

logger = logging.getLogger()

class API(Thread):

    def __init__(self):
        super().__init__(daemon=True)

    def run(self):
        app.run(
            host='0.0.0.0',
            port=5454,
            debug=False,
            threaded=True
        )


@app.route('/streams', methods=['GET'])
def streams():
    return state.get_service_setting('streamer', 'streams'), 200


@app.route('/stream/<string:file_name>', methods=['GET'])
@no_cache
def stream(file_name):
    stream_dir = os.path.abspath(state.get_global_setting('stream_dir'))
    return send_from_directory(directory=stream_dir, filename=file_name)


@app.route('/', methods=['GET'])
def index():
    data_dir = os.path.abspath(state.get_global_setting('data_dir'))
    stream_html = os.path.join(data_dir, 'index.html')
    return send_file(stream_html)
