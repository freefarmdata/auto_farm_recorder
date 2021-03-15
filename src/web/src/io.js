import io from 'socket.io-client';

const FARM_URL =  process.env.NODE_ENV === 'development' ? 'ws://127.0.0.1:5000/' : window.location.href;

let socket;

function start(onConnect, onDisconnect, onData) {
  console.log(`socket connecting to ${FARM_URL}`);

  socket = io(FARM_URL, {
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

export default {
  start,
  requestData,
  toggleService,
  restartService,
  selectModel,
  toggleWater,
};