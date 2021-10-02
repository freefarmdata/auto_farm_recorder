import React, { PureComponent } from 'react';
import service from '../../service';
import StreamPlayer from '../../stream';

class JSMpegWritableSource {
  constructor(url, options) {
    this.destination = null;
    this.completed = false;
    this.established = false;
    this.progress = 0;
    this.streaming = true;
  }

  connect(destination) {
    this.destination = destination;
  }

  start() {
    this.established = true;
    this.completed = true;
    this.progress = 1;
  }

  resume() {}

  destroy() {}

  write(data) {
    this.destination.write(data);
  }
}

class LiveStream extends PureComponent {

  constructor(props) {
    super(props);

    this.state = {
      streams: [],
      selectedStream: '',
      streamError: false,
      isLoading: false,
      isPlaying: false,
      showControls: false,
    }

    this.jsMpegPlayer = undefined;
    this.streamPlayer = new StreamPlayer();
    this.streamErrors = 0;
    this.onRefresh = this.onRefresh.bind(this);
    this.fetchStreams = this.fetchStreams.bind(this);
    this.onPlay = this.onPlay.bind(this);
    this.onStop = this.onStop.bind(this);
    this.onStreamData = this.onStreamData.bind(this);
    this.onStreamChange = this.onStreamChange.bind(this);
  }

  async componentDidMount() {
    await this.fetchStreams();

    // eslint-disable-next-line no-undef
    this.jsMpegPlayer = new JSMpeg.Player(null, {
			source: JSMpegWritableSource,
			audio: false,
			canvas: document.getElementById('stream'),
		});

    this.streamPlayer.on('update', (state) => {
      this.setState({
        isPlaying: state === 'playing',
        isLoading: state === 'loading'
      });
    });
    this.streamPlayer.on('data', this.onStreamData);
  }

  componentWillUnmount() {
    this.jsMpegPlayer = undefined;
    this.streamPlayer.destroy();
  }

  async fetchStreams() {
    const streams = await service.fetchStreams();
    if (streams) {
      this.setState({
        streams: streams,
        selectedStream: streams ? streams[0].stream_name : ''
      });
    }
  }

  onStreamData(chunk) {
    if (this.jsMpegPlayer) {
      try {
        this.jsMpegPlayer.source.write(chunk);
      } catch (err) {
        console.error(err);
        this.streamErrors += 1;
        if (this.streamErrors >= 100) {
          this.streamErrors = 0;
          this.setState({ streamError: true });
          this.onStop();
        }
      } 
    }
  }

  onStreamChange(event) {
    const selectedStream = event.target.value;

    this.setState({ selectedStream }, () => {
      this.onRefresh();
    });
  }

  onRefresh() {
    // eslint-disable-next-line no-undef
    this.jsMpegPlayer = new JSMpeg.Player(null, {
			source: JSMpegWritableSource,
			audio: false,
			canvas: document.getElementById('stream'),
		});

    this.onPlay();
  }

  onStop() {
    this.streamErrors = 0;
    this.setState({ streamError: false });
    this.streamPlayer.stop();
  }

  onPlay() {
    const { selectedStream } = this.state;
    if (selectedStream.length) {
      this.streamErrors = 0;
      this.setState({ streamError: false });
      this.streamPlayer.play(selectedStream);
    }
  }

  renderSelections() {
    const { streams, selectedStream } = this.state;

    return (
      <select value={selectedStream} onChange={this.onStreamChange}>
        {streams.map((stream, i) => {
          return (
            <option 
              key={i}
              value={stream.stream_name}>
              {stream.stream_name}
            </option>
          )
        })}
      </select>
    )
  }
  
  renderControls() {
    const { isPlaying, showControls } = this.state;

    if (showControls) {
      let playButton = <button onClick={this.onPlay}>&#9654;</button>;

      if (isPlaying) {
        playButton = <button onClick={this.onStop}>&#9607;</button>;
      }

      return (
        <div className="live-stream__controls">
          {playButton}
          <button onClick={this.onRefresh}>&#x21bb;</button>
        </div>
      )
    }
  }

  renderStreamError() {
    const { streamError } = this.state;

    if (streamError) {
      return (
        <div className="live-stream__error">
          Failed to play stream. Please retry.
        </div>
      )
    }
  }

  renderLoader() {
    const { isLoading } = this.state;

    if (isLoading) {
      return <div className="live-stream__loader spinner"></div>
    }
  }

  render() {
    return (
      <div className="live-stream">
        <h4>Live Streams</h4>
        <div
          className="live-stream__wrapper"
          onMouseEnter={() => this.setState({ showControls: true })}
          onMouseLeave={() => this.setState({ showControls: false })}>
          <canvas id="stream" className="live-stream__stream"></canvas>
          {this.renderControls()}
          {this.renderStreamError()}
          {this.renderLoader()}
        </div>
        
        <div className="live-stream__streams">
          {this.renderSelections()}
        </div>
      </div>
    );
  }
}

export default LiveStream;