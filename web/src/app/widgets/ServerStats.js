import React, { PureComponent } from 'react';

import mqtt from '../../mqtt';

class ServerStats extends PureComponent {

  constructor(props) {
    super(props);

    this.state = {
      stats: {},
    };

    this.onHeartbeat = this.onHeartbeat.bind(this);
  }

  async componentDidMount() {
    mqtt.subscribe('web/heartbeat/stats', this.onHeartbeat);
  }

  componentWillUnmount() {
    mqtt.unsubscribe('web/heartbeat/stats', this.onHeartbeat);
  }

  onHeartbeat(stats) {
    this.setState({ stats: JSON.parse(stats) });
  }

  render() {
    const { stats } = this.state;

    return (
      <div className="server-stats">
        <h4>Server Stats</h4>
        <div className="server-stats__container">
          <table>
            <thead>
              <tr>
                <th>stat</th>
                <th>value</th>
              </tr>
            </thead>
            <tbody>
              {Object.keys(stats).map((stat, i) => {
                return (
                  <tr key={i}>
                    <td>{stat}</td>
                    <td>{stats[stat]}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    );
  }
}

export default ServerStats;