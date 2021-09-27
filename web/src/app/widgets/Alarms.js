import React, { PureComponent } from 'react';
import * as moment from 'moment';

import mqtt from '../../mqtt.js';
import service from '../../service';

class Alarms extends PureComponent {

  constructor(props) {
    super(props);

    this.state = {
      alarms: {},
    };

    this.fetchAlarms = this.fetchAlarms.bind(this);
    this.onAlarms = this.onAlarms.bind(this);
    this.alarmInterval = undefined;
  }

  async componentDidMount() {
    await this.fetchAlarms();
    mqtt.subscribe('web/alarms/tx', this.onAlarms);
    this.alarmInterval = setInterval(async () => {
      await this.fetchAlarms();
    }, 10000);
  }

  componentWillUnmount() {
    mqtt.unsubscribe('web/alarms/tx', this.onAlarms);
    clearInterval(this.alarmInterval);
  }

  async fetchAlarms() {
    const alarms = await service.fetchActiveAlarms();
    if (alarms) {
      this.setState({ alarms });
    }
  }

  onAlarms(newAlarm) {
    const { alarms } = this.state;
    newAlarm = JSON.parse(newAlarm);

    alarms[newAlarm.id] = newAlarm;

    console.log(alarms);

    this.setState({ alarms: {...alarms} });
  }

  renderAlarms() {
    const { alarms } = this.state;

    return Object.values(alarms)
      .filter(alarm => alarm.active)
      .map((alarm, i) => {
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
                <span>{moment(alarm.time).format('dddd, MMM Do YYYY, h:mm:ss a')}</span>
              </div>
              {message}
            </div>
          </div>
        )
      })
  }

  render() {
    return (
      <div className="alarms">
        <h4>Alarms</h4>
        <div className="alarms__container">
          {this.renderAlarms()}
        </div>
      </div>
    );
  }
}

export default Alarms;