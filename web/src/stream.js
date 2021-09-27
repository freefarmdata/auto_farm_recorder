
import * as eio from 'engine.io-client';
import EventEmitter from 'events';

const RELAY_FARM_URL =  process.env.NODE_ENV === 'development' ? 'ws://127.0.0.1:5454/' : window.location.href;

export default class StreamPlayer extends EventEmitter {

    constructor(streamName) {
        super();
        this.streamName = streamName;
        this.url = RELAY_FARM_URL;
        this.socket = undefined;
        this._onMessage = this._onMessage.bind(this);
    }

    async play(callback) {
        console.log('stream socket', this.socket)
        if (!this.socket || this.socket.closed) {
            this.socket = this._newSocket();
            this.socket.send(this.streamName);
        }
        this.addListener('data', callback);
    }

    async refresh(callback) {
        this.pause();
        await this.play(callback);
    }

    pause() {
        this.removeAllListeners();
    }

    stop() {
        if (this.socket) {
            this.socket.close();
        }
        this.socket = undefined;
        this.removeAllListeners();
    }

    _newSocket() {
        const socket = new eio.Socket(RELAY_FARM_URL, { 
            upgrade: true,
        });
        socket.binaryType = 'arraybuffer';
        socket.on('open', () => {
            socket.closed = false;
            console.log('stream connected');
        });
        socket.on('close', (error) => {
            socket.closed = true;
            console.log('stream disconnected', error);
        })
        socket.on('error', (error) => {
            console.log('stream error', error);
        });
        return socket;
    }

    _onMessage(message) {
        if (!document.hidden && !isNaN(message.byteLength)) {
            this.emit('data', message);
        }
    }

}
