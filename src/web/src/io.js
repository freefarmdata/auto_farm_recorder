import io from 'socket.io-client';

const IO_FARM_URL =  process.env.NODE_ENV === 'development' ? 'ws://127.0.0.1:5000/' : window.location.href;

let socket;

function start(onConnect, onDisconnect, onData) {
  console.log(`socket connecting to ${IO_FARM_URL}`);

  socket = io(IO_FARM_URL, {
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 2000,
    reconnectionAttempts: Infinity,
    forceNew: true 
  });

  socket.on('connect', onConnect);

  socket.on('disconnect', () => {
    onDisconnect();
    socket.io.reconnect();
  });

  socket.on('connect_error', (err) => {
    onDisconnect();
    socket.io.reconnect();
  });

  socket.on('connect_timeout', (err) => {
    onDisconnect();
    socket.io.reconnect();
  });

  socket.on('uncaughtException', (err) => {
    onDisconnect();
    socket.io.reconnect();
  });

  socket.on('data', onData);
}

function requestData() {
  socket.emit('data', '');
}

function toggleService(service, state) {
  console.log('Toggle Service', service, state);
  socket.emit('toggle_service', { service, state })
}

function toggleWater(state) {
  console.log('Toggle Water', state);
  socket.emit('toggle_water', { state });
}

function restartService(service) {
  console.log('Restart Service', service);
  socket.emit('restart_service', { service })
}

function selectModel(name) {
  console.log('Select Model', name);
  socket.emit('select_model', { name })
}

function deleteModel(name) {
  console.log('Delete Model', name);
  socket.emit('delete_model', { name })
}

function trainModel(startTime, endTime) {
  console.log('Train Model', startTime, endTime);
  socket.emit('train_model', { startTime, endTime })
}

function updateServiceSetting(service_name, key, value) {
  console.log('Update Settings', service_name, key, value);
  socket.emit('update_setting', {  service_name, key, value })
}

function updateService(service_name, message) {
  console.log('Update Service', service_name, message);
  socket.emit('update_service', { service_name, message })
}

function syncSettingsToDisk() {
  console.log('sync settings');
  socket.emit('sync_settings', '');
}

export default {
  start,
  requestData,
  toggleService,
  restartService,
  selectModel,
  deleteModel,
  toggleWater,
  trainModel,
  updateServiceSetting,
  updateService,
  syncSettingsToDisk
};