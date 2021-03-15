import React, { Component } from 'react';

class Status extends Component {
  constructor(props) {
    super(props);
    this.state = {
      services: [],
    };
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.status) {
      const services = Object.keys(nextProps.status).map((key) => {
        return { name: key, status: nextProps.status[key] };
      });

      this.setState({ services: services });
    }
  }

  render() {
    return (
      <div className="status">
        <h2>Service Status</h2>
        <div className="status__container">
          {this.state.services.map((service, i) => {
            return (
              <span key={i} className="status__tag">
                <span className="status__tag__name">{service.name}</span>
                <span className={`status__tag__dot ${service.status}`}>
                </span>
              </span>
            )
          })}
        </div>
      </div>
    );
  }
}

export default Status;