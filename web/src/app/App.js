import React, { Component } from 'react';
import mqtt from '../mqtt';

import LiveStream from './widgets/LiveStream';
import EditSettings from './widgets/EditSettings';
import ToggleServices from './widgets/ToggleServices';
import Alarms from './widgets/Alarms';
import ServerStats from './widgets/ServerStats';
import Sensors from './widgets/Sensors';

class App extends Component {
  constructor(props) {
    super(props);

    this.state = {
      connected: false,
    };

    this.onConnect = this.onConnect.bind(this);
    this.onDisconnect = this.onDisconnect.bind(this);
  }

  componentDidMount() {
    mqtt.initialize();
    mqtt.subscribe('connected', this.onConnect);
    mqtt.subscribe('disconnected', this.onDisconnect);
  }

  componentWillUnmount() {
    mqtt.unsubscribe('connected', this.onConnect);
    mqtt.unsubscribe('disconnected', this.onDisconnect);
  }

  onConnect() {
    this.setState({ connected: true });
  }

  onDisconnect() {
    this.setState({ connected: false });
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
      <>
        {this.renderConnectionLabel()}
        <div className="grid">
          <div className="grid__layout">
            <Alarms />
            <ServerStats />
            <LiveStream />
            <ToggleServices />
            <EditSettings />
            <Sensors />
          </div>
        </div>
      </>
    );
  }
}

export default App;