const engine = require('engine.io');
const dgram = require('dgram');

const streams = require('./streams');
const config = require('./config');
const conflator = require('./conflator');

let eioServer;
let relays = [];

function broadcast(streamName, message) {
    for (const sid in eioServer.clients) {
        const client = eioServer.clients[sid];
        if (client.state && client.state.stream === streamName) {
            client.send(message);
        }
    }
}

function streamIsRequested(streamName) {
    for (const sid in eioServer.clients) {
        const client = eioServer.clients[sid];
        if (client.state && client.state.stream === streamName) {
            return true;
        }
    }
    return false;
}

function onVideoMessage(stream) {
    return (packet) => {
        broadcast(stream.stream_name, packet);
    }
}

async function createRelay(stream) {
    const server = dgram.createSocket('udp4');
    const callback = onVideoMessage(stream);

    return await new Promise((resolve) => {
        server.bind(stream.stream_port, '0.0.0.0', () => {
            return resolve({
                stream,
                server,
                callback
            });
        })
    });
}

function toggleRelays() {
    for (const group of relays) {
        const { server, stream, callback } = group;
        const hasListener = server.eventNames().includes('message');
        const streamRequested = streamIsRequested(stream.stream_name);
        if (streamRequested && !hasListener) {
            console.log('attaching relay for stream', stream);
            server.addListener('message', callback);
        } else if (!streamRequested && hasListener) {
            console.log('removing relay for stream', stream);
            server.removeListener('message', callback);
        }
    }
}

function onConnection(socket) {
    console.log('client connected');

    socket.state = {
        stream: undefined,
    };

    socket.on('message', (message) => {
        const stream = streams.getStreams().find(stream => stream.stream_name === message);
        if (stream) {
            console.log('client requesting stream', stream);
            socket.state.stream = stream.stream_name;
        }
    });
    socket.on('close', () => {
        if (eioServer.clients[socket.sid]) {
            delete eioServer.clients[socket.sid];
        }
        console.log('client disconnected');
    })
}

function conflate(socket, messages) {
    if (messages.length > config.maxWriteBuffer) {
        console.log('conflating messages');
        return [];
    }

    return messages;
}

async function initialize(httpServer) {
    eioServer = engine.attach(httpServer, {
        pingTimeout: 2000,
        pingInterval: 10000,
        allowEIO3: true,
        httpCompression: false,
        cors: {
            credentials: true,
            origin: (_, cb) => cb(null, true),
        }
    });

    eioServer.on('connection', onConnection);
    eioServer.on('flush', conflator(conflate));

    relays = await Promise.all(streams.getStreams().map(createRelay));

    setInterval(toggleRelays, 1000);
}

module.exports = {
    initialize,
    broadcast,
    streamIsRequested
}