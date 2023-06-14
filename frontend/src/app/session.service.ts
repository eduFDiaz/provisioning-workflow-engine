import { Injectable } from '@angular/core';
import { CookieService } from 'ngx-cookie-service';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SessionService {

  private requestID = new Subject<string>();
  public requestID$ = this.requestID.asObservable();

  constructor(private cookieService: CookieService) { 
    let request_id = this.getSessionVar("request-id");
    console.log("SessionService constructor: request_id = " + request_id);
    this.requestID.next(request_id);
  }

  public getSessionVar(key: string): string {
    let value = this.cookieService.get(key);
    console.log("Getting session param: " + key + " = " + value);
    return value;
  }

  public setSessionVar(key: string, value: string, date: Date): void {
    console.log("Setting session param: " + key + " to " + value);
    this.cookieService.set(key, value, date);
    this.requestID.next(value);
  }

}
