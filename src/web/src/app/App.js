import React, { Component } from 'react';

import io from '../io';

import Actions from './Actions';
import Status from './Status';
import Info from './Info';

class App extends Component {
  constructor(props) {
    super(props);

    this.state = {
      data: {},
      connected: false,
    };

    this.ioInterval = undefined;
    this.onConnect = this.onConnect.bind(this);
    this.onDisconnect = this.onDisconnect.bind(this);
    this.onData = this.onData.bind(this);
  }

  componentDidMount() {
    io.start(this.onConnect, this.onDisconnect, this.onData);
  }

  componentWillUnmount() {
    if (this.ioInterval) {
      clearInterval(this.ioInterval);
    }
  }

  onConnect() {
    console.log('connected')
    this.setIOInterval();
    this.setState({ connected: true });
  }

  onDisconnect() {
    console.log('disconnected')
    this.setState({ connected: false });
    if (this.ioInterval) {
      clearInterval(this.ioInterval);
    }
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
        <Status status={this.state.data.status} />
        <Info info={this.state.data.info} />
        <Actions
          status={this.state.data.status}
          info={this.state.data.info}
          selectModel={(name) => {
            io.selectModel(name);
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
        />
      </div>
    );
  }
}

export default App;