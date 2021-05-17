import React, { PureComponent } from 'react';

import io from '../../io';

class DisableServices extends PureComponent {
  render() {
    const { status, info } = this.props.data;

    if (!status || !info?.settings) {
      return <div className="spinner"></div>;
    }

    return (
      <div className="disable-services">
        <h4>Disable Services</h4>
        <div className="disable-services__container">
          {Object.keys(status).map((serviceName, i) => {
            return (
              <label key={i}>
                <input
                  type="checkbox"
                  checked={info.settings[serviceName]['disabled']}
                  onChange={() => {}}
                  onClick={() => io.disableService(serviceName)}
                />
                {serviceName}
              </label>
            )
          })}
        </div>
      </div>
    );
  }
}

export default DisableServices;