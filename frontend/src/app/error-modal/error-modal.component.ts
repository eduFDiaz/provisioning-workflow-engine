import { AfterViewInit, Component, EventEmitter, OnDestroy, OnInit, Output } from '@angular/core';
import { HttpService } from '../milestone-http-service.service';
import { SessionService } from '../session.service';
import {ClrDatagridSortOrder} from '@clr/angular';

@Component({
  selector: 'app-error-modal',
  templateUrl: './error-modal.component.html',
  styleUrls: ['./error-modal.component.scss']
})
export class ErrorModalComponent implements OnInit, OnDestroy, AfterViewInit{
  // requestID: string = "712714d1-e22c-49aa-b036-a786e1e82516";
  requestID: string = this.session.getSessionVar('request-id');
  errors: any[] = [];
  @Output() toggle = new EventEmitter();
  descSort = ClrDatagridSortOrder.DESC;
  constructor(private httpService: HttpService, private session: SessionService) { 

  }

  ngOnInit(): void {}
  ngOnDestroy(): void {}

  ngAfterViewInit(): void {
    if (this.requestID !== undefined && this.requestID != "") {
      this.getErrors();
    }
    this.session.requestID$.subscribe((requestID: string) => {
      this.requestID = requestID;
      this.getErrors();
    });
  }

  getErrors() {
    this.httpService.getErrors(this.requestID).subscribe((errors: any) => {
      this.errors = errors;
      console.log(this.errors);
    });
  }

  toggleModal() {
    this.toggle.emit();
  }
}
