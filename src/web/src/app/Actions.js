import React, { Component } from 'react';
import moment from 'moment';

class Actions extends Component {

  constructor(props) {
    super(props);

    this.state = {
      modelTrainStart: '',
      modelTrainEnd: '',
    };
  }

  renderStatuses() {
    const { status } = this.props;

    if (!status) {
      return;
    }

    return Object.keys(status).map((serviceName, i) => {
      return (
        <button
          key={i}
          onClick={() => {
            this.props.restartService(serviceName);
          }}
        >
          {serviceName}
        </button>
      )
    });
  }

  renderToggle() {
    const { status } = this.props;

    if (!status) {
      return;
    }

    return Object.keys(status).map((serviceName, i) => {
      return (
        <span key={i}>
          <span>{serviceName}</span>
          <div>
            <button
              onClick={(event) => {
                this.props.toggleService(serviceName, true);
              }}
            >
              Online
            </button>
            <button
              onClick={(event) => {
                this.props.toggleService(serviceName, false);
              }}
            >
              Offline
            </button>
          </div>
        </span>
      )
    });
  }

  renderWater() {
    const { info } = this.props;

    if (!info) {
      return;
    }

    let notifier = null;
    if (info.watering_set && info.watering_start) {
      notifier = <span className="notifier">{moment(info.watering_start).fromNow()}</span>
    }

    let times = null;
    if (info.watering_times && info.watering_times.length > 0) {
      times = (
        <table>
          <thead>
            <tr>
              <th>Start</th>
              <th>End</th>
              <th>Elapsed</th>
            </tr>
          </thead>
          <tbody>
            {info.watering_times.map((time, i) => {
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

    return (
      <>
        <label className="switch">
          <input
            type="checkbox"
            checked={info.watering_set}
            onChange={() => {}}
            onClick={(event) => {
              this.props.toggleWater(event.target.checked);
            }}
          />
          <span className="slider"></span>
        </label>
        {notifier}
        {times}
      </>
    );
  }

  renderSelectModel() {
    const { info } = this.props;

    if (!info || !info.soil_models.length) {
      return;
    }

    return (
      <div className="actions__block">
      <h4>Select A Soil Model</h4>
      <div className="actions__block--sservice">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Start</th>
                <th>End</th>
                <th>Error</th>
                <th>Activate</th>
                <th>Delete</th>
              </tr>
            </thead>
            <tbody>
              {info.soil_models.map((model, i) => {
                return (
                  <tr key={i} className={model.active.toString()}>
                    <td>{model.name}</td>
                    <td>{moment(model.start_time*1E3).format('dddd, MMM Do YYYY, h:mm:ss a')}</td>
                    <td>{moment(model.end_time*1E3).format('dddd, MMM Do YYYY, h:mm:ss a')}</td>
                    <td>{model.error.toFixed(5)}</td>
                    <td>
                      <button
                        onClick={() => {
                          this.props.selectModel(model.name);
                        }}
                      >
                        Select
                      </button>
                    </td>
                    <td>
                      <button
                        onClick={() => {
                          this.props.deleteModel(model.name);
                        }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  renderTrainModel() {
    return (
      <div className="actions__block">
        <h4>Train A Soil Model</h4>
        <div className="actions__block--tservice">
          <input
            type="datetime-local"
            onChange={(e) => {
              this.setState({ modelTrainStart: moment(e.target.value) });
            }}
          />
          <input
            type="datetime-local"
            onChange={(e) => {
              this.setState({ modelTrainEnd: moment(e.target.value) });
            }}
          />
          <button
            onClick={() => {
              const { modelTrainStart, modelTrainEnd } = this.state;
              if (modelTrainStart && modelTrainEnd && modelTrainEnd.isAfter(modelTrainStart)) {
                this.props.onTrainModel(
                  modelTrainStart.unix(),
                  modelTrainEnd.unix()
                );
              }
            }}
          >
            Train
          </button>
        </div>
      </div>
    );
  }

  render() {
    return (
      <div className="actions">
        <h2>Actions</h2>
        <div className="actions__container">
          <div className="actions__block">
            <h4>Restart Service</h4>
            <div className="actions__block--rservice">
              {this.renderStatuses()}
            </div>
          </div>
          <div className="actions__block">
            <h4>Toggle Service</h4>
            <div className="actions__block--tservice">
              {this.renderToggle()}
            </div>
          </div>
          <div className="actions__block">
            <h4>Toggle Watering Event</h4>
            <div className="actions__block--wservice">
              {this.renderWater()}
            </div>
          </div>
          {this.renderSelectModel()}
          {this.renderTrainModel()}
        </div>
      </div>
    );
  }
}

export default Actions;