import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import { Observer } from 'rxjs/Observer';
import { Message } from '../model/message';

import * as socketIo from 'socket.io-client';

@Injectable()
export class SocketService {
    private socket;

    public initSocket(url: string): void {
        this.socket = socketIo(url);
    }

    public send(message: Message): void {
        this.socket.emit('message', message);
    }

    public onMessage(): Observable<Message> {
        return new Observable<Message>(observer => {
            this.socket.on('message',     (data: Message) => {
              observer.next(data);
            });
        });
    }
}
