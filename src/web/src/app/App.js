import React, { Component } from 'react';

import io from '../io';

import Actions from './Actions';
import Status from './Status';
import Tags from './Tags';
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
    this.clearIntervals = this.clearIntervals.bind(this);
    this.onData = this.onData.bind(this);
  }

  componentDidMount() {
    io.start(
      this.onConnect,
      this.onDisconnect,
      this.onData,
    );
  }

  componentWillUnmount() {
    this.clearIntervals();
  }

  clearIntervals() {
    clearInterval(this.ioInterval);
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
  }

  onData(data) {
    this.setState({ data });
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
        <Image image={this.state.image} />
        <Status status={this.state.data.status} />
        <Tags tags={this.state.data.tags} />
        <Actions
          status={this.state.data.status}
          tags={this.state.data.tags}
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
          onUpdateServiceSetting={(service_name, key, value) => {
            io.updateServiceSetting(service_name, key, value);
          }}
          onUpdateService={(service_name, message) => {
            io.updateService(service_name, message);
          }}
          onSyncSettingsToDisk={() => {
            io.syncSettingsToDisk();
          }}
        />
      </div>
    );
  }
}

export default App;