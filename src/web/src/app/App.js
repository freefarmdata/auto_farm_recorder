import React, { Component } from 'react';

import io from '../io';

import Actions from './Actions';
import Status from './Status';
import Info from './Info';
import Image from './Image';

class App extends Component {
  constructor(props) {
    super(props);

    this.state = {
      data: {},
      image: {},
      connected: false,
    };

    this.ioInterval = undefined;
    this.onConnect = this.onConnect.bind(this);
    this.onDisconnect = this.onDisconnect.bind(this);
    this.onLatestImage = this.onLatestImage.bind(this);
    this.clearIntervals = this.clearIntervals.bind(this);
    this.onData = this.onData.bind(this);
  }

  componentDidMount() {
    io.start(
      this.onConnect,
      this.onDisconnect,
      this.onData,
      this.onLatestImage
    );
  }

  componentWillUnmount() {
    this.clearIntervals();
  }

  clearIntervals() {
    clearInterval(this.ioInterval);
    clearInterval(this.imageInterval);
  }

  onConnect() {
    console.log('connected')
    this.clearIntervals();
    this.setIOInterval();
    this.setState({ connected: true });
  }

  onDisconnect() {
    console.log('disconnected')
    this.setState({ connected: false });
    this.clearIntervals();
  }

  setIOInterval() {
    this.ioInterval = setInterval(() => {
      io.requestData();
    }, 1000);
    this.imageInterval = setInterval(() => {
      const { image } = this.state;
      io.getLatestImage(image ? image['time'] : undefined);
    }, 10000);
  }

  onData(data) {
    this.setState({ data });
  }

  onLatestImage(image) {
    this.setState({ image });
  }

  renderConnectionLabel() {
    const { connected } = this.state;

    const label = connected ? 'Connected' : 'Disconnected';

    return (
      <div className={`clabel ${connected}`}>
        {label}
      </div>
    );
  }

  render() {
    return (
      <div>
        {this.renderConnectionLabel()}
        <Status status={this.state.data.status} />
        <Info info={this.state.data.info} />
        <Image image={this.state.image} />
        <Actions
          status={this.state.data.status}
          info={this.state.data.info}
          selectModel={(name) => {
            io.selectModel(name);
          }}
          deleteModel={(name) => {
            io.deleteModel(name);
          }}
          toggleService={(service, state) => {
            io.toggleService(service, state);
          }}
          toggleWater={(state) => {
            io.toggleWater(state);
          }}
          restartService={(service) => {
            io.restartService(service);
          }}
          onTrainModel={(startTime, endTime) => {
            io.trainModel(startTime, endTime);
          }}
        />
      </div>
    );
  }
}

export default App;