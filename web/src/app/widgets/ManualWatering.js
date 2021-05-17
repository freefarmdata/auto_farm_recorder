import React, { PureComponent } from 'react';
import * as moment from 'moment';

import io from '../../io';
import service from '../../service';

class ManualWatering extends PureComponent {

  constructor(props) {
    super(props);
    
    this.state = {
      watering_times: []
    };
  }

  componentDidMount() {
    this.fetchWateringTimes();
  }

  async fetchWateringTimes() {
    const watering_times = await service.fetchWateringTimes();
    this.setState({ watering_times });
  }

  renderToggle() {
    const { tags } = this.props.data;

    let notifier = null;
    if (tags && tags.watering_set && tags.watering_start) {
      notifier = `(${moment(tags.watering_start).fromNow()})`
    }

    return (
      <div className="switcher">
        <label className="switch">
          <input
            type="checkbox"
            defaultChecked={tags.watering_set}
            onChange={() => {}}
            onClick={(event) => {
              io.toggleWater(event.target.checked);
            }}
          />
          <span className="slider"></span>
        </label>
        Set Watering {notifier}
      </div>
    );
  }

  renderRefresh() {
    return (
      <button
        onClick={() => {
          this.fetchWateringTimes();
        }}
      >
        Refresh
      </button>
    )
  }

  renderTable() {
    const { watering_times } = this.state;

    return (
      <table>
        <thead>
          <tr>
            <th>Start</th>
            <th>End</th>
            <th>Elapsed</th>
          </tr>
        </thead>
        <tbody>
          {watering_times.map((time, i) => {
            const start = moment(time.start_time*1E3);
            const end = moment(time.end_time*1E3);
            const dur = moment.duration(end - start);

            return (
              <tr key={i}>
                <td>{start.format('dddd, MMM Do YYYY, h:mm:ss a')}</td>
                <td>{end.format('dddd, MMM Do YYYY, h:mm:ss a')}</td>
                <td>{dur.humanize()}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    );
  }

  render() {
    const { tags, info } = this.props.data;

    if (!tags || !info) {
      return <div className="spinner"></div>;
    }

    return (
      <div className="manual-watering">
        <h4>Manual Watering</h4>
        <div className="manual-watering__container">
          <div className="manual-watering__container__header">
            {this.renderToggle()}
            {this.renderRefresh()}
          </div>
          {this.renderTable()}
        </div>
      </div>
    );
  }
}

export default ManualWatering;