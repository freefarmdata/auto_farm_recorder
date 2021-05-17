import React, { Component } from 'react';

import io from '../io';

import Grid from './Grid';

class App extends Component {
  constructor(props) {
    super(props);

    this.state = {
      connected: false,
      data: {},
    };

    this.ioInterval = undefined;
    this.clearIntervals = this.clearIntervals.bind(this);
    this.onConnect = this.onConnect.bind(this);
    this.onDisconnect = this.onDisconnect.bind(this);
    this.onData = this.onData.bind(this);
  }

  componentDidMount() {
    io.initialize();
    io.subscribe('connect', this.onConnect);
    io.subscribe('disconnect', this.onDisconnect);
    io.subscribe('data', this.onData);
  }

  componentWillUnmount() {
    this.clearIntervals();
    io.unsubscribe('connect', this.onConnect);
    io.unsubscribe('disconnect', this.onDisconnect);
    io.unsubscribe('data', this.onData);
  }
  
  onData(data) {
    this.setState({ data: data || {} });
  }

  onConnect() {
    this.clearIntervals();
    this.setIOInterval();
    this.setState({ connected: true });
  }

  onDisconnect() {
    this.clearIntervals();
    this.setState({ connected: false });
  }

  clearIntervals() {
    clearInterval(this.ioInterval);
  }

  setIOInterval() {
    this.ioInterval = setInterval(() => {
      io.requestData();
    }, 1000);
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
        <Grid data={this.state.data} />
      </div>
    );
  }
}

/**
 * <Image image={this.state.image} />
        <Status status={this.state.data.status} />
        <Tags tags={this.state.data.tags} />
        <Actions
          status={this.state.data.status}
          tags={this.state.data.tags}
          info={this.state.data.info}
          selectModel={io.selectModel}
          deleteModel={io.deleteModel}
          toggleService={io.toggleService}
          toggleWater={io.toggleWater}
          disableService={io.disableService}
          onTrainModel={io.trainModel}
          onUpdateServiceSetting={io.updateServiceSetting}
          onUpdateService={io.updateService}
          onSyncSettingsToDisk={io.syncSettingsToDisk}
        />
 */

export default App;