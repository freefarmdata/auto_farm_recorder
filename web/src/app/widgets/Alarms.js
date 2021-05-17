import React, { PureComponent } from 'react';
import * as moment from 'moment';

import io from '../../io.js';
import service from '../../service';

class Alarms extends PureComponent {

  constructor(props) {
    super(props);

    this.state = {
      alarms: {},
    };

    this.onAlarm = this.onAlarm.bind(this);
  }

  async componentDidMount() {
    await this.fetchAlarms();
    io.subscribe('alarm', this.onAlarm);
  }

  componentWillUnmount() {
    io.unsubscribe('alarm', this.onAlarm);
  }

  async fetchAlarms() {
    const alarms = await service.fetchActiveAlarms();
    this.setState({ alarms });
  }

  onAlarm(alarm) {
    const { alarms } = this.state;

    alarms[alarm.id] = alarm;

    this.setState({ alarms });
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
                <span>{moment(alarm.time*1000).format('dddd, MMM Do YYYY, h:mm:ss a')}</span>
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