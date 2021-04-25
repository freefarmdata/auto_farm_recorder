import React, { PureComponent } from 'react';

const HTTP_FARM_URL =  process.env.NODE_ENV === 'development' ? 'http://127.0.0.1:5000' : window.location.href;
class Image extends PureComponent {
  render() {
    return (
      <div className="image">
        <h2>Latest Snapshot</h2>
        <div className="image__wrapper">
          <img
            src={`${HTTP_FARM_URL}/api/stream`}
            alt="video stream"
          />
        </div>
      </div>
    );
  }
}

export default Image;