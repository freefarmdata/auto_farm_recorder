import React, { PureComponent } from 'react';

const HTTP_FARM_URL =  process.env.NODE_ENV === 'development' ? 'http://127.0.0.1:5000' : window.location.href;

class LiveStream extends PureComponent {

  constructor(props) {
    super(props);

    this.state = {
      refresh: false,
    }

    this.runRefresh = this.runRefresh.bind(this);
  }

  runRefresh() {
    this.setState({ refresh: true }, () => {
      this.setState({ refresh: false });
    });
  }

  renderStream() {
    const { refresh, hide } = this.state;

    if (!refresh && !hide) {
      return (
        <img
          src={`${HTTP_FARM_URL}/api/stream`}
          alt="video stream"
        />
      );
    }
  }

  render() {
    return (
      <div className="live-stream">
        <button onClick={this.runRefresh}>Refresh</button>
        <div className="live-stream__image">{this.renderStream()}</div>
      </div>
    );
  }
}

export default LiveStream;