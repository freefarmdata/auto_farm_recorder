import EventEmitter from 'events';
import * as mqtt from 'paho-mqtt';

const MQTT_FARM_URL = process.env.NODE_ENV === 'development' ? '127.0.0.1' : window.location.hostname;

let client;
const mqttEmitter = new EventEmitter();

function subscribe(event, callback) {
  mqttEmitter.addListener(event, callback);
};

function unsubscribe(event, callback) {
  mqttEmitter.removeListener(event, callback);
}

function initialize() {
  console.log(`client connecting to ${MQTT_FARM_URL}`);

  client = new mqtt.Client(MQTT_FARM_URL, 9001, '/mqtt', '1234');

  client.connect({
    timeout: 10,
    onSuccess: onConnect,
    onFailure: onDisconnect,
    reconnect: true,
  });
}

function onConnect() {
  mqttEmitter.emit('connected');
  client.onConnectionLost = onDisconnect;
  client.onMessageArrived = onMessage;
  client.subscribe('web/alarms/tx');
  client.subscribe('web/heartbeat/#');
  client.subscribe('web/board/#');
}

function onDisconnect() {
  mqttEmitter.emit('disconnected');
}

function onMessage(message) {
  console.log('mqtt packet:', message.topic);
  mqttEmitter.emit(message.topic, message.payloadString);
}


export default {
  initialize: initialize,
  subscribe: subscribe,
  unsubscribe: unsubscribe,
};