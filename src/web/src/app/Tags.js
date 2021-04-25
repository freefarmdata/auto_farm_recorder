import React, { Component } from 'react';


function isDefined(value) {
  return value !== null && value !== undefined;
}

class Tags extends Component {

  renderInfo() {
    const { tags } = this.props;

    if (!tags) {
      return;
    }

    return Object.keys(tags)
      .map((key, i) => {
        let label = isDefined(tags[key]) ? tags[key] : 'n/a';
        label = typeof label === 'number' ? label.toFixed(4).toString() : label.toString();

        return (
          <span key={i} className="info__tag">
            <span className="info__tag__name">{key}</span>
            <span className="info__tag__label">{label}</span>
          </span>
        )
      });
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

export default Tags;