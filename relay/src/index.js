const http = require('http');

const socket = require('./socket');
const streams = require('./streams');
const config = require('./config');

async function main() {
    console.info('loaded configurations', JSON.stringify(config));
    
    const httpServer = http.createServer();

    await streams.initialize();
    await socket.initialize(httpServer);

    httpServer.listen(5454, () => {
        console.log('relay started');
    });
}

main();