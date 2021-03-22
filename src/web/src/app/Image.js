import React, { PureComponent } from 'react';

class Image extends PureComponent {
  render() {
    return (
      <div className="image">
        <h2>Latest Snapshot</h2>
        <div className="image__wrapper">
          <img
            src={`data:image/png;base64,${this.props.image['image']}`}
            alt="latest snapshot"
          />
        </div>
      </div>
    );
  }
}

export default Image;