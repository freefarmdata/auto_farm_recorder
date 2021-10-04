import React, { PureComponent } from 'react';
import * as moment from 'moment';

import mqtt from '../../mqtt.js';
import service from '../../service';

class Alarms extends PureComponent {

  constructor(props) {
    super(props);

    this.state = {
      alarms: {},
      loading: false,
    };

    this.onClearAlarm = this.onClearAlarm.bind(this);
    this.fetchAlarms = this.fetchAlarms.bind(this);
    this.onAlarms = this.onAlarms.bind(this);
    this.alarmInterval = undefined;
  }

  componentDidMount() {
    this.fetchAlarms();
    mqtt.subscribe('web/alarms/tx', this.onAlarms);
    this.alarmInterval = setInterval(async () => {
      await this.fetchAlarms();
    }, 10000);
  }

  componentWillUnmount() {
    mqtt.unsubscribe('web/alarms/tx', this.onAlarms);
    clearInterval(this.alarmInterval);
  }

  fetchAlarms() {
    this.setState({ loading: true }, async () => {
      const alarms = await service.fetchActiveAlarms();
      if (alarms) {
        this.setState({ alarms, loading: false });
      }
    });
  }

  onAlarms(newAlarm) {
    const { alarms } = this.state;
    newAlarm = JSON.parse(newAlarm);
    alarms[newAlarm.id] = newAlarm;
    this.setState({ alarms: {...alarms}, loading: false });
  }

  onClearAlarm(alarm) {
    this.setState({ loading: true }, async () => {
      await service.clearAlarm(alarm.id);
      this.setState({ loading: false });
    });
  }

  renderAlarms() {
    const { alarms } = this.state;

    const activeAlarms = Object.values(alarms).filter(alarm => alarm.active);

    if (activeAlarms.length <= 0) {
      return (
        <div className="alarm__none">
          No active alarms
        </div>
      );
    }

    return activeAlarms.map((alarm, i) => {
        const wrapperClasses = `alarm ${alarm.level}`;
        const statusClasses = `alarm__status ${alarm.level}`;

        let message = null;
        if (alarm.message) {
          message = <p>{alarm.message}</p>;
        }

        return (
          <div className={wrapperClasses} key={i}>
            <div className={statusClasses}></div>
            <div className="alarm__content">
              <div className="alarm__content__title">
                <h4>{alarm.name}</h4>
                <span>{moment(alarm.time).fromNow()}</span>
                <button onClick={() => this.onClearAlarm(alarm)}>
                  x
                </button>
              </div>
              {message}
            </div>
          </div>
        )
      })
  }

  renderLoading() {
    const { loading } = this.state;

    if (loading) {
      return <div className="spinner alarms__loader"></div>
    }
  }

  render() {
    return (
      <div className="alarms">
        <h4>Alarms</h4>
        {this.renderLoading()}
        <div className="alarms__container">
          {this.renderAlarms()}
        </div>
      </div>
    );
  }
}

export default Alarms;