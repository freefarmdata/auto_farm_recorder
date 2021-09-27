import React, { PureComponent } from 'react';

import io from '../../io';
import mqtt from '../../mqtt';
import service from '../../service';

class ToggleServices extends PureComponent {

  constructor(props) {
    super(props);

    this.state = {
      status: undefined,
    }

    this.fetchStatus = this.fetchStatus.bind(this);
    this.onStatus = this.onStatus.bind(this);
    this.onClickOff = this.onClickOff.bind(this);
    this.onClickOn = this.onClickOn.bind(this);
    this.statusInterval = undefined;
  }

  async componentDidMount() {
    await this.fetchStatus();
    mqtt.subscribe('web/heartbeat/status', this.onStatus);
    this.statusInterval = setInterval(async () => {
      await this.fetchStatus();
    }, 10000);
  }

  componentWillUnmount() {
    mqtt.unsubscribe('web/heartbeat/status', this.onStatus);
    clearInterval(this.statusInterval);
  }

  onStatus(status) {
    console.log('status', JSON.parse(status));
  }

  async fetchStatus() {
    const status = await service.fetchServiceStatus();
    if (status) {
      console.log(status);
      this.setState({ status });
    }
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

  render() {
    const { status } = this.state;

    if (!status) {
      return <div className="spinner"></div>;
    }

    return (
      <div className="toggle-services">
        <h4>Toggle Services</h4>
        <div className="toggle-services__container">
          {Object.keys(status).map((serviceName, i) => {
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