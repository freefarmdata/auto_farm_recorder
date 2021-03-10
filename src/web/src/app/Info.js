import React, { Component } from 'react';

class Info extends Component {
  constructor(props) {
    super(props);
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.info) {
      const info = Object.keys(nextProps.info).map((key) => {
        return { name: key, label: nextProps.info[key] };
      });
  
      this.setState({ info: info });
    }
  }

  renderInfo() {
    const { info } = this.props;

    if (!info) {
      return;
    }

    return Object.keys(info)
      .map((key, i) => {
        if (typeof info[key] !== 'object') {
          return (
            <span key={i} className="info__tag">
              <span className="info__tag__name">{key}</span>
              <span className="info__tag__label">{info[key] ? info[key] : 'n/a'}</span>
            </span>
          )
        }
      })
      .filter((component) => component);
  }

  render() {
    return (
      <div className="info">
        <h3>Info Status</h3>
        <div className="info__container">
          {this.renderInfo()}
        </div>
      </div>
    );
  }
}

export default Info;