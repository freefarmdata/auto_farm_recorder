import EventEmitter from 'events';
import * as mqtt from 'paho-mqtt';
import { format } from 'path';

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
  client.subscribe('web/#');
}

function onDisconnect() {
  mqttEmitter.emit('disconnected');
}

function onMessage(message) {
  const splits = message.topic.split('/');

  //web/board/mock_client/soil
  //web/board/mock_client
  //web/board

  for (let i = 0; i < splits.length; i++) {
    const parts = splits.slice(0, splits.length - i);
    if (parts.length === 1) {
      break;
    }
    mqttEmitter.emit(parts.join('/'), message.payloadString);
  }
}


export default {
  initialize: initialize,
  subscribe: subscribe,
  unsubscribe: unsubscribe,
};