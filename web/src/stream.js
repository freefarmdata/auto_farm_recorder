
import * as eio from 'engine.io-client';
import EventEmitter from 'events';

const RELAY_FARM_URL =  process.env.NODE_ENV === 'development' ? 'ws://127.0.0.1:5454/' : window.location.href;

export default class StreamPlayer extends EventEmitter {

    constructor() {
        super();
        this.url = RELAY_FARM_URL;
        this.streamName = undefined;
        this.socket = undefined;
        this._isPlaying = false;
        this._onMessage = this._onMessage.bind(this);
        this._onStop = this._onStop.bind(this);
        this._onPlay = this._onPlay.bind(this);

        this.on('play', this._onPlay);
        this.on('stop', this._onStop);
    }

    play(streamName) {
        this.streamName = streamName;
        this.emit('play');
    }

    stop() {
        this.emit('stop');
    }

    destroy() {
        this.removeAllListeners();
    }

    _onPlay() {
        if (this.socket) {
            this.socket.close();
        }
        this.socket = undefined;
        this.socket = this._newSocket();
        this.emit('update', 'loading');
    }

    _onStop() {
        if (this.socket) {
            this.socket.close();
        }
        this.socket = undefined;
        this.emit('update', 'stopped');
    }

    _newSocket() {
        const socket = new eio.Socket(RELAY_FARM_URL, { 
            upgrade: true,
        });
        socket.binaryType = 'arraybuffer';
        socket.on('open', () => {
            socket.send(this.streamName);
            socket.on('message', this._onMessage);
        });
        socket.on('close', (error) => {
            this._isPlaying = false;
            this.emit('update', 'stopped');
        });
        return socket;
    }

    _onMessage(message) {
        if (!this._isPlaying) {
            this.emit('update', 'playing');
        }

        this._isPlaying = true;
        if (!document.hidden && !isNaN(message.byteLength)) {
            this.emit('data', message);
        }
    }

}
