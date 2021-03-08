import React, { Component } from 'react';

class Info extends Component {
  constructor(props) {
    super(props);
    this.state = {
      info: [],
    };
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.info) {
      const info = Object.keys(nextProps.info).map((key) => {
        return { name: key, label: nextProps.info[key] };
      });
  
      this.setState({ info: info });
    }
  }

  render() {
    return (
      <div className="info">
        <h3>Info Status</h3>
        <div className="info__container">
          {this.state.info.map((info, i) => {
            return (
              <span key={i} className="info__tag">
                <span className="info__tag__name">{info.name}</span>
                <span className="info__tag__label">{info.label ? info.label : 'n/a'}</span>
              </span>
            )
          })}
        </div>
      </div>
    );
  }
}

export default Info;