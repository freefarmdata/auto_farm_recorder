
module.exports = {
    environment: process.env.NODE_ENV || 'local',
    recorderURL: process.env.RECORDER_URL || 'http://0.0.0.0:5000',
    maxWriteBuffer: process.env.MAX_WRITE_BUFFER || 100
}