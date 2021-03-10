import React, { Component } from 'react';

class Actions extends Component {
  constructor(props) {
    super(props);
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
          <label className="switch">
            <input
              type="checkbox"
              checked={status[serviceName]}
              onChange={() => {}}
              onClick={(event) => {
                this.props.toggleService(serviceName, event.target.checked);
              }}
            />
            <span className="slider"></span>
          </label>
        </span>
      )
    });
  }

  renderWater() {
    const { info } = this.props;

    if (!info) {
      return;
    }

    return (
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
    );
  }

  renderSelectModel() {
    const { info } = this.props;

    if (!info || !info.soil_models.length) {
      return;
    }

    return info.soil_models.map((model, i) => {
      return (
        <span key={i}>
          <p>{model.name}</p>
          <table>
            <tbody>
              <tr>
                <td>train time start</td>
                <td>{model.start}</td>
              </tr>
              <tr>
                <td>train time end</td>
                <td>{model.start}</td>
              </tr>
              <tr>
                <td>mean squared error</td>
                <td>{model.error}</td>
              </tr>
            </tbody>
          </table>
          <button
            onClick={() => {
              this.props.selectModel(model.name);
            }}
          >
            Select
          </button>
        </span>
      )
    });
  }

  render() {
    return (
      <div className="actions">
        <h3>Actions</h3>
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
            <div>
              {this.renderWater()}
            </div>
          </div>
          <div className="actions__block">
            <h4>Select A Soil Model</h4>
            <div className="actions__block--sservice">
              {this.renderSelectModel()}
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default Actions;