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
      stream: '',
      play: false,
    }

    this.player = undefined;
    this.streamPlayer = undefined;
    this.onRefresh = this.onRefresh.bind(this);
    this.fetchStreams = this.fetchStreams.bind(this);
    this.onPlay = this.onPlay.bind(this);
    this.onPause = this.onPause.bind(this);
    this.onStreamData = this.onStreamData.bind(this);
    this.onStreamChange = this.onStreamChange.bind(this);
  }

  async componentDidMount() {
    await this.fetchStreams();
    // eslint-disable-next-line no-undef
    this.player = new JSMpeg.Player(null, {
			source: JSMpegWritableSource,
			audio: false,
			canvas: document.getElementById('stream'),
		});
  }

  componentWillUnmount() {
    this.player = undefined;
    if (this.streamPlayer) {
      this.streamPlayer.stop();
      this.streamPlayer = undefined;
    }
  }

  async fetchStreams() {
    const streams = await service.fetchStreams();
    if (streams) {
      this.setState({ streams });
    }
  }

  onStreamData(chunk) {
    console.log(chunk);
    if (this.player) {
      this.player.source.write(chunk);
    }
  }

  async onStreamChange(event) {
    const stream = event.target.value;

    this.setState({ stream }, async () => {
      await this.onRefresh();
    });
  }

  async onRefresh() {
    const { stream } = this.state.stream;

    // eslint-disable-next-line no-undef
    this.player = new JSMpeg.Player(null, {
			source: JSMpegWritableSource,
			audio: false,
			canvas: document.getElementById('stream'),
		});

    if (this.streamPlayer) {
      this.streamPlayer.stop();
      this.streamPlayer = undefined;
    }

    if (stream && stream.length) {
      this.streamPlayer = new StreamPlayer(stream);
      await this.streamPlayer.play(this.onStreamData);
    }
  }

  onPause() {
    if (this.streamPlayer) {
      this.streamPlayer.pause();
    }
  }

  async onPlay() {
    const { stream } = this.state;

    if (stream && stream.length && (!this.streamPlayer || (this.streamPlayer && this.streamPlayer.streamName !== stream))) {
      this.streamPlayer = new StreamPlayer(stream);
    }

    if (this.streamPlayer) {
      await this.streamPlayer.play(this.onStreamData);
    }
  }

  renderSelections() {
    const { streams, stream } = this.state;

    return (
      <select value={stream} onChange={this.onStreamChange}>
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

  render() {
    return (
      <div className="live-stream">
        <canvas id="stream" className="live-stream__stream"></canvas>
        <div className="live-stream__controls">
          <button onClick={this.onPlay}>&#9654;</button>
          <button onClick={this.onPause}>&#9868;</button>
          <button onClick={this.onRefresh}>&#8635;</button>
          {this.renderSelections()}
        </div>
      </div>
    );
  }
}

export default LiveStream;