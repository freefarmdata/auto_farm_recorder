const engine = require('engine.io');

const config = require('./config');
const conflator = require('./conflator');

let server;

function streamIsRequested(streamName) {
    for (const sid in server.clients) {
        const client = server.clients[sid];
        if (client.state && client.state.stream === streamName) {
            return true;
        }
    }
    return false;
}

function broadcast(streamName, message) {
    for (const sid in server.clients) {
        const client = server.clients[sid];
        if (client.state && client.state.stream === streamName) {
            client.send(message);
        }
    }
}

function onConnection(socket) {
    console.log('client connected');

    socket.state = {};
    socket.state.stream = 'frontcam';

    socket.on('message', (message) => {
        console.log('message', message);
    });
}

function conflate(socket, messages) {
    if (messages.length > config.maxWriteBuffer) {
        console.log('conflating messages');
        return [];
    }

    return messages;
}

function initialize(httpServer) {
    server = engine.attach(httpServer, {
        pingTimeout: 2000,
        pingInterval: 10000,
        allowEIO3: true,
        httpCompression: false,
        cors: {
            credentials: true,
            origin: (_, cb) => cb(null, true),
        }
    });

    server.on('connection', onConnection);
    server.on('flush', conflator(conflate));
}

module.exports = {
    initialize,
    broadcast,
    streamIsRequested
}