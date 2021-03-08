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

  render() {
    return (
      <div className="actions">
        <h3>Actions</h3>
        <div className="actions__container">
          
          <div className="actions__block">
            <h4>Toggle Watering Event</h4>
            <div>
              <label className="switch">
                <input type="checkbox" />
                <span className="slider"></span>
              </label>
            </div>
          </div>

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

        </div>
      </div>
    );
  }
}

export default Actions;