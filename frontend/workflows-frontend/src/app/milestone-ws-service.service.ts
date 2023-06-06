import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class MilestoneWsService {
  socket!: WebSocket;

  public connect(url: string): Observable<string> {
    this.socket = new WebSocket(url);
    console.log('Connecting to ' + url);

    return new Observable<string>(observer => {
      this.socket.onmessage = event => observer.next(event.data);
      this.socket.onerror = event => observer.error(event);
      this.socket.onclose = event => observer.complete();
    });
  }

  public send(data: string): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(data);
    }
  }

  public close(): void {
    if (this.socket) {
      this.socket.close();
    }
  }
}
