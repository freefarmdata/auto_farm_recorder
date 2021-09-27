import io from 'socket.io-client';
import EventEmitter from 'events';

const IO_FARM_URL =  process.env.NODE_ENV === 'development' ? 'ws://127.0.0.1:5000/' : window.location.href;

let socket;
const ioEmitter = new EventEmitter();

function subscribe(event, callback) {
  ioEmitter.addListener(event, callback);
};

function unsubscribe(event, callback) {
  ioEmitter.removeListener(event, callback);
}

function initialize() {
  console.log(`socket connecting to ${IO_FARM_URL}`);

  socket = io(IO_FARM_URL, {
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 2000,
    reconnectionAttempts: Infinity,
    forceNew: true 
  });

  socket.on('connect', () => {
    ioEmitter.emit('connect');
  });

  socket.on('disconnect', () => {
    ioEmitter.emit('disconnect');
    socket.io.reconnect();
  });

  socket.on('connect_error', (err) => {
    ioEmitter.emit('disconnect');
    socket.io.reconnect();
  });

  socket.on('connect_timeout', (err) => {
    ioEmitter.emit('disconnect');
    socket.io.reconnect();
  });

  socket.on('uncaughtException', (err) => {
    ioEmitter.emit('disconnect');
    socket.io.reconnect();
  });

  socket.on('data', (data) => {
    ioEmitter.emit('data', data);
  });

  socket.on('alarm', (alarm) => {
    ioEmitter.emit('alarm', alarm);
  });
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

function disableService(service_name) {
  console.log('Disable Service', service_name);
  socket.emit('disable_service', { service_name })
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
  initialize,
  subscribe,
  unsubscribe,
};