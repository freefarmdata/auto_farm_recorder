import React, { PureComponent } from 'react';

import io from '../../io';

class ToggleServices extends PureComponent {
  render() {
    const { status } = this.props.data;

    if (!status) {
      return <div className="spinner"></div>;
    }

    return (
      <div className="toggle-services">
        <h4>Toggle Services</h4>
        <div className="toggle-services__container">
          {Object.keys(status).map((serviceName, i) => {
            const classNames = `${status[serviceName]}`;
            return (
              <span className={classNames} key={i}>
                <span>{serviceName}</span>
                <div>
                  <button
                    onClick={(event) => {
                      io.toggleService(serviceName, true);
                    }}
                  >
                    On
                  </button>
                  <button
                    onClick={(event) => {
                      io.toggleService(serviceName, false);
                    }}
                  >
                    Off
                  </button>
                </div>
              </span>
            )
          })}
        </div>
      </div>
    );
  }
}

export default ToggleServices;