const dgram = require('dgram');
const util = require('util');
const socket = require('./socket');
const streams = require('./streams');

function onMessage(stream) {
    return (packet) => {
        socket.broadcast(stream.stream_name, packet);
    }
}

async function createRelay(stream) {
    const server = dgram.createSocket('udp4');
    const callback = onMessage(stream);

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

module.exports.initialize = async function() {
    const servers = await Promise.all(
        streams.getStreams().map(createRelay)
    );

    setInterval(() => {
        for (const group of servers) {
            const { server, stream, callback } = group;
            const hasListener = server.eventNames().includes('message');
            const streamRequested = socket.streamIsRequested(stream.stream_name);
            if (streamRequested && !hasListener) {
                server.addListener('message', callback);
            } else if (!streamRequested && hasListener) {
                server.removeListener('message', callback);
            }
        }
    }, 1000);
}