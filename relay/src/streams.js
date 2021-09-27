const axios = require('axios');
const config = require('./config');

let streams = [];

async function fetchStreams() {
    if (config.environment === 'local') {
        return [{
            stream_name: 'frontcam',
            stream_port: 8083
        }];
    }

    const response = await axios.get(`${config.recorderURL}/api/streams`);
    return response.data;
}

module.exports.getStreams = function() {
    return streams;
}

module.exports.initialize = async function() {
    streams = await fetchStreams();
    console.info('fetched streams', JSON.stringify(streams));
}