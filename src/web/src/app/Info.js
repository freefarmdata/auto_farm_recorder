import React, { Component } from 'react';


function isDefined(value) {
  return value !== null && value !== undefined;
}

class Info extends Component {
  constructor(props) {
    super(props);
  }

  renderInfo() {
    const { info } = this.props;

    if (!info) {
      return;
    }

    return Object.keys(info)
      .map((key, i) => {
        if (!Array.isArray(info[key])) {

          let label = isDefined(info[key]) ? info[key] : 'n/a';
          label = typeof label === 'number' ? label.toFixed(4).toString() : label.toString();

          return (
            <span key={i} className="info__tag">
              <span className="info__tag__name">{key}</span>
              <span className="info__tag__label">{label}</span>
            </span>
          )
        }
      })
      .filter((component) => component);
  }

  render() {
    return (
      <div className="info">
        <h2>Info Status</h2>
        <div className="info__container">
          {this.renderInfo()}
        </div>
      </div>
    );
  }
}

export default Info;