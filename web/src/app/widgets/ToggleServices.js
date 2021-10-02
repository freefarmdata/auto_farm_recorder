import React, { PureComponent } from 'react';

import io from '../../io';
import mqtt from '../../mqtt';
import service from '../../service';

class ToggleServices extends PureComponent {

  constructor(props) {
    super(props);

    this.state = {
      status: undefined,
      loading: false,
    }

    this.fetchStatus = this.fetchStatus.bind(this);
    this.onStatus = this.onStatus.bind(this);
    this.onClickOff = this.onClickOff.bind(this);
    this.onClickOn = this.onClickOn.bind(this);
    this.statusInterval = undefined;
  }

  componentDidMount() {
    this.fetchStatus();
    mqtt.subscribe('web/heartbeat/status', this.onStatus);
    this.statusInterval = setInterval(() => {
      this.fetchStatus();
    }, 10000);
  }

  componentWillUnmount() {
    mqtt.unsubscribe('web/heartbeat/status', this.onStatus);
    clearInterval(this.statusInterval);
  }

  onStatus(status) {
    this.setState({ status: JSON.parse(status), loading: false });
  }

  fetchStatus() {
    this.setState({ loading: true }, async () => {
      const status = await service.fetchServiceStatus();
      if (status) {
        this.setState({ status, loading: false });
      }
    });
  }

  async onClickOff(serviceName) {
    const okay = await service.deactivateService(serviceName);
    if (okay) {
      const { status } = this.state;
      status[serviceName] = false;
      this.setState({ status: {...status} });
    }
  }

  async onClickOn(serviceName) {
    const okay = await service.activateService(serviceName);
    if (okay) {
      const { status } = this.state;
      status[serviceName] = true;
      this.setState({ status: {...status} });
    }
  }

  renderLoading() {
    const { loading } = this.state;

    if (loading) {
      return <div className="spinner toggle-services__loader"></div>
    }
  }

  render() {
    const { status } = this.state;

    return (
      <div className="toggle-services">
        <h4>Toggle Services</h4>
        {this.renderLoading()}
        <div className="toggle-services__container">
          {Object.keys(status || {}).sort().map((serviceName, i) => {
            const classNames = `${status[serviceName]}`;
            return (
              <span className={classNames} key={i}>
                <span>{serviceName}</span>
                <div>
                  <button onClick={(event) => this.onClickOn(serviceName)}>
                    On
                  </button>
                  <button onClick={(event) => this.onClickOff(serviceName)}>
                    Off
                  </button>
                </div>
              </span>
            )
          })}
        </div>
      </div>
    );
  }
}

export default ToggleServices;