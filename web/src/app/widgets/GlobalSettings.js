import React, { PureComponent } from 'react';

import io from '../../io';

class GlobalSettings extends PureComponent {

  render() {
    const { info } = this.props.data;

    if (!info?.settings?.camera && !info?.settings?.global) {
      return <div className="spinner"></div>;
    }

    const { sunrise, sunset } = info.settings.global;
    const { interval, save_frame } = info.settings.camera;
    const dInterval = interval / 1E9;
    const dSaveFrame = save_frame / 1E9;

    return (
      <div className="global-settings">
        <h4>Global Settings</h4>
        <div className="global-settings__container">
          <button
            onClick={() => io.syncSettingsToDisk()}
          >
            Sync Settings To Disk
          </button>
          <div className="range">
            <span>Camera FPS: {dInterval}s</span>
            <input
              type="range"
              defaultValue={dInterval}
              onChange={(event) => {
                io.updateService('camera', {
                  'action': 'set_interval',
                  'interval': event.target.value * 1E9
                });
              }}
              step="0.05"
              min="0.01"
              max="5"
            />
          </div>
          <div className="range">
            <span>Camera Save: {dSaveFrame}s</span>
            <input
              type="range"
              defaultValue={dSaveFrame}
              onChange={(event) => {
                io.updateServiceSetting('camera', 'save_frame', event.target.value * 1E9)
              }}
              step="5"
              min="0"
              max="600"
            />
          </div>
          <div className="input">
            <span>Sunrise</span>
            <input
              type="text"
              defaultValue={sunrise}
              onKeyDown={(event) => {
                if (event.code === 'Enter') {
                  io.updateServiceSetting('global', 'sunrise', event.target.value);
                }
              }}
            />
          </div>
          <div className="input">
            <span>Sunset</span>
            <input
              type="text"
              defaultValue={sunset}
              onKeyDown={(event) => {
                if (event.code === 'Enter') {
                  io.updateServiceSetting('global', 'sunset', event.target.value);
                }
              }}
            />
          </div>
        </div>
      </div>
    );
  }
}

export default GlobalSettings;