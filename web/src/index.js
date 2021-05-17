import React from 'react';
import ReactDOM from 'react-dom';

import './styles/index.css';
import './styles/gridster.css';
import './styles/grid.css';
import './styles/switch.css';
import './styles/graphs.css';

import './styles/disable-services.css';
import './styles/toggle-services.css';
import './styles/global-settings.css';
import './styles/manual-watering.css';
import './styles/live-stream.css';
import './styles/alarms.css';

import App from './app/App';

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);
